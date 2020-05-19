import logging
import threading
import time
from multiprocessing import Pool as ThreadPool
from typing import List, Optional, Tuple

from django.contrib.gis.gdal import CoordTransform, SpatialReference
from django.contrib.gis.geos import LineString, Point
from django.contrib.gis.geos.collections import MultiPolygon
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.db import InternalError
from django.db.utils import OperationalError
from shapely.geometry import Polygon as ShapelyPolygon

from config.settings.base import env
from ohdm_django_mapnik.ohdm.postgis_utily import (
    make_polygon_valid,
    set_polygon_way_area,
)
from ohdm_django_mapnik.ohdm.tags2mapnik import (
    cleanup_tags,
    fill_osm_object,
    get_z_order,
    is_road,
)

from .models import (
    OhdmGeoobjectLine,
    OhdmGeoobjectPoint,
    OhdmGeoobjectPolygon,
    PlanetOsmLine,
    PlanetOsmPoint,
    PlanetOsmPolygon,
    PlanetOsmRoads,
)

logger = logging.getLogger(__name__)


class GEOMETRY_TYPE:
    POINT = "point"
    LINE = "line"
    POLYGON = "polygon"

    TYPES = [POINT, LINE, POLYGON]


class SaveCache2DB(threading.Thread):
    def __init__(
        self,
        point_cache: List[PlanetOsmPoint],
        line_cache: List[PlanetOsmLine],
        road_cache: List[PlanetOsmRoads],
        polygon_cache: List[PlanetOsmPolygon],
    ):

        threading.Thread.__init__(self)
        self.point_cache: List[PlanetOsmPoint] = point_cache
        self.line_cache: List[PlanetOsmLine] = line_cache
        self.road_cache: List[PlanetOsmRoads] = road_cache
        self.polygon_cache: List[PlanetOsmPolygon] = polygon_cache

    def run(self):
        print(threading.activeCount())
        if self.point_cache:
            self.save_points()
        if self.line_cache:
            self.save_lines()
        if self.road_cache:
            self.save_roads()
        if self.polygon_cache:
            self.save_polygons()

    def save_points(self):
        try:
            PlanetOsmPoint.objects.bulk_create(self.point_cache)
            self.point_cache.clear()
        except OperationalError as e:
            logger.warning(e)
            time.sleep(2)
            self.save_points()

    def save_lines(self):
        try:
            PlanetOsmLine.objects.bulk_create(self.line_cache)
            self.line_cache.clear()
        except OperationalError as e:
            logger.warning(e)
            time.sleep(2)
            self.save_lines()

    def save_roads(self):
        try:
            PlanetOsmRoads.objects.bulk_create(self.road_cache)
            self.road_cache.clear()
        except OperationalError as e:
            logger.warning(e)
            time.sleep(2)
            self.save_roads()

    def save_polygons(self):
        try:
            PlanetOsmPolygon.objects.bulk_create(self.polygon_cache)
            self.polygon_cache.clear()
        except OperationalError as e:
            logger.warning(e)
            time.sleep(2)
            self.save_polygons()


class Ohdm2Mapnik:
    """
    convert ohdm database schema to mapnik readable Osm2pgsql schema

    -> https://wiki.openstreetmap.org/wiki/Osm2pgsql/schema
    """

    # https://docs.djangoproject.com/en/3.0/ref/contrib/gis/gdal/#coordtransform
    CT: CoordTransform = CoordTransform(SpatialReference(4326), SpatialReference(3857))

    def __init__(
        self,
        chunk_size: int = 10000,
        geometries: List[str] = ["point", "line", "polygon"],
        sql_threads: int = 1,
        convert_threads: int = 1,
    ):
        """
        setup Ohdm2Mapnik class
        
        Keyword Arguments:
            chunk_size {int} -- how many entries will be load at once from database (default: {10000})
            continue_old_import {bool} -- If set, from the source server will be set an offset of the hight of the traget db (default: {False})
            geometries {List[str]} -- which geometries should be process (default: {["point", "line", "polygon"])})
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

        # geometries to be process
        self.geometries: List[str] = geometries

        # number of threats
        self.sql_threads: int = sql_threads

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
        logger.info(
            "Points: {} | Lines/Polygon: {} | Multipolygon: {}".format(
                self.point_counter, self.line_counter, self.polygon_counter
            )
        )

    def check_cache_save(self):
        if (
            self.point_counter
            + self.line_counter
            + self.point_counter
            + self.polygon_counter
        ) % self.chunk_size == 0:
            self.save_cache()

    def save_cache(self):
        logger.info("saving cache ...")

        while threading.activeCount() > self.sql_threads:
            time.sleep(0.1)

        save_cache_2_db: SaveCache2DB = SaveCache2DB(
            point_cache=self.point_cache.copy(),
            line_cache=self.line_cache.copy(),
            road_cache=self.road_cache.copy(),
            polygon_cache=self.polygon_cache.copy(),
        )

        save_cache_2_db.start()

        self.point_cache.clear()
        self.line_cache.clear()
        self.road_cache.clear()
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
        if geo_type == GEOMETRY_TYPE.POINT:
            where_statement = "geoobject_geometry.type_target = 0 or geoobject_geometry.type_target = 1"
        elif geo_type == GEOMETRY_TYPE.LINE:
            where_statement = "geoobject_geometry.type_target = 2"
        else:
            where_statement = "geoobject_geometry.type_target = 3"

        return """
                SELECT 
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
                WHERE {1};
            """.format(
            geo_type, where_statement, env.str("OHDM_SCHEMA")
        )

    def convert_points(self):
        ohdm_object: OhdmGeoobjectPoint
        for ohdm_object in OhdmGeoobjectPoint.objects.all().iterator(
            chunk_size=self.chunk_size
        ):
            self.point_counter += 1

            point: Optional[PlanetOsmPoint] = self.convert_point(
                ohdm_object=ohdm_object
            )
            if point:
                self.point_cache.append(point)

            if self.point_counter % self.chunk_size == 0:
                self.show_status()
                self.save_cache()

        self.show_status()
        self.save_cache()

    def convert_point(
        self, ohdm_object: OhdmGeoobjectPoint
    ) -> Optional[PlanetOsmPoint]:
        try:
            if GEOSGeometry(ohdm_object.way).geom_type != "Point":
                return None
        except TypeError:
            return None

        if not ohdm_object.tags:
            ohdm_object.tags = {}

        if ohdm_object.classification_class and ohdm_object.classification_subclassname:
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
        return fill_osm_object(osm_object=point)

    def convert_lines(self):
        ohdm_object: OhdmGeoobjectLine
        for ohdm_object in OhdmGeoobjectLine.objects.all().iterator(
            chunk_size=self.chunk_size
        ):
            self.line_counter += 1

            line: Tuple[
                Optional[PlanetOsmLine], Optional[PlanetOsmRoads]
            ] = self.convert_line(ohdm_object=ohdm_object)
            if line[0]:
                self.line_cache.append(line[0])
            if line[1]:
                self.road_cache.append(line[1])

            if self.line_counter % self.chunk_size == 0:
                self.show_status()
                self.save_cache()

        self.show_status()
        self.save_cache()

    def convert_line(
        self, ohdm_object: OhdmGeoobjectLine,
    ) -> Tuple[Optional[PlanetOsmLine], Optional[PlanetOsmRoads]]:
        try:
            if GEOSGeometry(ohdm_object.way).geom_type != "LineString":
                return None
        except TypeError:
            return None

        if not ohdm_object.tags:
            ohdm_object.tags = {}

        if ohdm_object.classification_class and ohdm_object.classification_subclassname:
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

        if is_road(tags=clean_tags):
            return (line, line.to_road())

        return (line, None)

    def convert_polygons(self):

        ohdm_object: OhdmGeoobjectPolygon
        for ohdm_object in OhdmGeoobjectPolygon.objects.all().iterator(
            chunk_size=self.chunk_size
        ):
            self.polygon_counter += 1

            polygon: Optional[PlanetOsmPolygon] = self.convert_polygon(
                ohdm_object=ohdm_object
            )
            if polygon:
                self.polygon_cache.append(polygon)

            if self.polygon_counter % self.chunk_size == 0:
                self.show_status()
                self.save_cache()

        self.show_status()
        self.save_cache()

    def convert_polygon(
        self, ohdm_object: OhdmGeoobjectPolygon,
    ) -> Optional[PlanetOsmPolygon]:
        try:
            # geometry: GEOSGeometry = GEOSGeometry(ohdm_object.way,)
            geometry: GEOSGeometry = GEOSGeometry(ohdm_object.way, srid=4326)
            # print(GEOSGeometry(ohdm_object.way).coords)
            if geometry.geom_type != "Polygon" and geometry.geom_type != "MultiPolygon":
                print(geometry.geom_type)
                return None
        except TypeError:
            return None

        if not ohdm_object.tags:
            ohdm_object.tags = {}

        if ohdm_object.classification_class and ohdm_object.classification_subclassname:
            ohdm_object.tags[
                ohdm_object.classification_class
            ] = ohdm_object.classification_subclassname

        clean_tags: dict = cleanup_tags(tags=ohdm_object.tags)

        polygon: PlanetOsmPolygon = PlanetOsmPolygon(
            way=geometry,
            geoobject=ohdm_object.geoobject_id,
            name=ohdm_object.name,
            valid_since=ohdm_object.valid_since,
            valid_until=ohdm_object.valid_until,
            tags=clean_tags,
            z_order=get_z_order(tags=clean_tags),
            way_area=geometry.area,
        )

        return fill_osm_object(osm_object=polygon)

    def run(self):
        """
        convert ohdm database to mapnik readable tables
        """
        # iterate through every ohdm entry
        for geometry in self.geometries:
            logger.info("Start to convert {} objects".format(geometry))
            if geometry == GEOMETRY_TYPE.POINT:
                self.convert_points()
            elif geometry == GEOMETRY_TYPE.LINE:
                self.convert_lines()
            else:
                self.convert_polygons()
                # self.update_polygons()

            self.save_cache()
            logger.info("{} is done!".format(geometry))

        # wait to be all threats are done
        while threading.activeCount() > 1:
            time.sleep(0.1)

        logger.info("All data are converted!")
