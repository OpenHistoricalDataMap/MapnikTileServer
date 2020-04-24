import logging
import time
from typing import List

from config.settings.base import env
from ohdm_django_mapnik.ohdm.postgis_utily import (make_polygon_valid,
                                                   set_polygon_way_area)
from ohdm_django_mapnik.ohdm.tags2mapnik import (cleanup_tags, fill_osm_object,
                                                 get_z_order, is_road)

from .models import (OhdmGeoobjectWay, PlanetOsmLine, PlanetOsmPoint,
                     PlanetOsmPolygon, PlanetOsmRoads)

logger = logging.getLogger(__name__)


class Ohdm2Mapnik:
    """
    convert ohdm database schema to mapnik readable Osm2pgsql schema

    -> https://wiki.openstreetmap.org/wiki/Osm2pgsql/schema
    """

    def __init__(self, chunk_size: int = 10000, continue_old_import: bool = False, geometries: List[str] = ["points", "lines", "polygons"]):
        """
        setup Ohdm2Mapnik class
        
        Keyword Arguments:
            chunk_size {int} -- how many entries will be load at once from database (default: {10000})
            continue_old_import {bool} -- If set, from the source server will be set an offset of the hight of the traget db (default: {False})
            geometries {List[str]} -- which geometries should be process (default: {["points", "lines", "polygons"]})
        """
        self.chunk_size: int = chunk_size

        self.point_cache: List[PlanetOsmPoint] = []
        self.line_cache: List[PlanetOsmLine] = []
        self.road_cache: List[PlanetOsmRoads] = []
        self.polygon_cache: List[PlanetOsmPolygon] = []

        self.point_counter: int = 0
        self.line_counter: int = 0
        self.polygon_counter: int = 0

        # process start time
        self.start_time: float = 0

        # continue old ohdm2mapnik command
        self.continue_old_import: bool = continue_old_import

        # geometries to be process
        self.geometries: List[str] = geometries

    def display_process_time(self):
        """
        display process time
        """

        row: int = self.point_counter + self.line_counter + self.polygon_counter

        process_time: float = time.time() - self.start_time

        if process_time <= 360:  # 6 minutes
            logger.info("--- {} rows in {:4.3f} seconds ---".format(row, process_time))
        elif process_time <= 7200:  # 120 minutes
            logger.info(
                "--- {} rows in {:4.3f} minutes ---".format(row, process_time / 60)
            )
        else:
            logger.info(
                "--- {} rows in {:4.3f} hours ---".format(row, process_time / 360)
            )

    def show_status(self):
        if (self.point_counter + self.line_counter + self.point_counter) % 10000 == 0:
            logger.info(
                "Points: {} | Lines/Polygon: {} | Multipolygon: {}".format(
                    self.point_counter, self.line_counter, self.polygon_counter
                )
            )

    def check_cache_save(self):
        if (
            self.point_counter + self.line_counter + self.point_counter
        ) % self.chunk_size == 0:
            self.save_cache()

    def save_cache(self):
        logger.info("saving cache ...")
        if self.point_cache:
            PlanetOsmPoint.objects.bulk_create(self.point_cache)
            self.point_cache.clear()
        if self.line_cache:
            PlanetOsmLine.objects.bulk_create(self.line_cache)
            self.line_cache.clear()
        if self.road_cache:
            PlanetOsmRoads.objects.bulk_create(self.road_cache)
            self.road_cache.clear()
        if self.polygon_cache:
            PlanetOsmPolygon.objects.bulk_create(self.polygon_cache)
            self.polygon_cache.clear()

    def update_polygons(self):
        logger.info("Make invalid polygons valid!")
        make_polygon_valid()
        logger.info("Set way_area for all polygons!")
        set_polygon_way_area()

    def generate_sql_query(self, geo_type: str, offset: int = 0) -> str:
        """
        Generate SQL Query to fetch the request geo objects
        
        Arguments:
            offset {int} -- geo_type as string like point, line or polygon
        
        Returns:
            str -- SQL query as string
        """

        where_statement: str = ""
        if geo_type == OhdmGeoobjectWay.GEOMETRY_TYPE.POINT:
            where_statement = "geoobject_geometry.type_target = 0 or geoobject_geometry.type_target = 1"
        elif geo_type == OhdmGeoobjectWay.GEOMETRY_TYPE.LINE:
            where_statement = "geoobject_geometry.type_target = 2"
        else:
            where_statement = "geoobject_geometry.type_target = 3"

        return """
                SELECT 
                    {0}s.id as way_id,
                    geoobject_geometry.id_geoobject_source as geoobject_id,
                    geoobject.name,
                    classification.class as classification_class,
	                classification.subclassname as classification_subclassname,
                    geoobject_geometry.tags,
                    geoobject_geometry.valid_since,
                    geoobject_geometry.valid_until,
                    {0}s.{0} as way
                FROM {2}.{0}s
                INNER JOIN {2}.geoobject_geometry ON {0}s.id=geoobject_geometry.id_target
                INNER JOIN {2}.geoobject ON geoobject_geometry.id_geoobject_source=geoobject.id
                INNER JOIN {2}.classification ON geoobject_geometry.classification_id=classification.id
                WHERE {1}
                ORDER BY geoobject.id
                OFFSET {3};
            """.format(
            geo_type, where_statement, env.str("OHDM_SCHEMA"), offset
        )

    def convert_points(self, geometry: str):

        offset: int = 0
        if self.continue_old_import:
            offset = PlanetOsmPoint.objects.all().count()

        ohdm_object: OhdmGeoobjectWay
        for ohdm_object in (
            OhdmGeoobjectWay.objects.using("ohdm")
            .raw(self.generate_sql_query(geo_type=geometry, offset=offset))
            .iterator()
        ):
            self.point_counter += 1
            if not ohdm_object.tags:
                ohdm_object.tags = {}

            if (
                ohdm_object.classification_class
                and ohdm_object.classification_subclassname
            ):
                ohdm_object.tags[
                    ohdm_object.classification_class
                ] = ohdm_object.classification_subclassname

            clean_tags: dict = cleanup_tags(tags=ohdm_object.tags)

            point: PlanetOsmPoint = PlanetOsmPoint(
                way=ohdm_object.way,
                geoobject=ohdm_object.geoobject_id,
                name=ohdm_object.name,
                valid_since=ohdm_object.valid_since,
                valid_until=ohdm_object.valid_until,
                tags=clean_tags,
            )
            point = fill_osm_object(osm_object=point)
            self.point_cache.append(point)

            self.show_status()
            self.check_cache_save()

    def convert_lines(self, geometry: str):

        offset: int = 0
        if self.continue_old_import:
            offset = PlanetOsmLine.objects.all().count()

        ohdm_object: OhdmGeoobjectWay
        for ohdm_object in (
            OhdmGeoobjectWay.objects.using("ohdm")
            .raw(self.generate_sql_query(geo_type=geometry, offset=offset))
            .iterator()
        ):
            self.line_counter += 1
            if not ohdm_object.tags:
                ohdm_object.tags = {}

            if (
                ohdm_object.classification_class
                and ohdm_object.classification_subclassname
            ):
                ohdm_object.tags[
                    ohdm_object.classification_class
                ] = ohdm_object.classification_subclassname

            clean_tags: dict = cleanup_tags(tags=ohdm_object.tags)

            line: PlanetOsmLine = PlanetOsmLine(
                way=ohdm_object.way,
                geoobject=ohdm_object.geoobject_id,
                name=ohdm_object.name,
                valid_since=ohdm_object.valid_since,
                valid_until=ohdm_object.valid_until,
                tags=clean_tags,
                z_order=get_z_order(tags=clean_tags),
            )
            line = fill_osm_object(osm_object=line)
            self.line_cache.append(line)

            if is_road(tags=clean_tags):
                self.road_cache.append(line.to_road())

            self.show_status()
            self.check_cache_save()

    def convert_polygons(self, geometry: str):

        offset: int = 0
        if self.continue_old_import:
            offset = PlanetOsmPolygon.objects.all().count()

        ohdm_object: OhdmGeoobjectWay
        for ohdm_object in (
            OhdmGeoobjectWay.objects.using("ohdm")
            .raw(self.generate_sql_query(geo_type=geometry, offset=offset))
            .iterator()
        ):
            self.polygon_counter += 1
            if not ohdm_object.tags:
                ohdm_object.tags = {}

            if (
                ohdm_object.classification_class
                and ohdm_object.classification_subclassname
            ):
                ohdm_object.tags[
                    ohdm_object.classification_class
                ] = ohdm_object.classification_subclassname

            clean_tags: dict = cleanup_tags(tags=ohdm_object.tags)

            polygon: PlanetOsmPolygon = PlanetOsmPolygon(
                way=ohdm_object.way,
                geoobject=ohdm_object.geoobject_id,
                name=ohdm_object.name,
                valid_since=ohdm_object.valid_since,
                valid_until=ohdm_object.valid_until,
                tags=clean_tags,
                z_order=get_z_order(tags=clean_tags),
            )
            polygon = fill_osm_object(osm_object=polygon)
            self.polygon_cache.append(polygon)

            self.show_status()
            self.check_cache_save()

    def run(self):
        """
        convert ohdm database to mapnik readable tables
        """
        # iterate through every ohdm entry
        for geometry in self.geometries:
            logger.info("Start to convert {} objects".format(geometry))
            if geometry == OhdmGeoobjectWay.GEOMETRY_TYPE.POINT:
                self.convert_points(geometry=geometry)
            elif geometry == OhdmGeoobjectWay.GEOMETRY_TYPE.LINE:
                self.convert_lines(geometry=geometry)
            else:
                self.convert_polygons(geometry=geometry)
                self.update_polygons()

            self.save_cache()
            logger.info("{} is done!".format(geometry))

        logger.info("All data are converted!")
