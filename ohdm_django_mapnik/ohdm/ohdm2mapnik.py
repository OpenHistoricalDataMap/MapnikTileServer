import time
from datetime import datetime
from multiprocessing.pool import ThreadPool
from typing import Any, List

from django.db import connections

from config.settings.base import env
from ohdm_django_mapnik.ohdm.postgis_utily import (make_polygon_valid,
                                                   set_polygon_way_area)
from ohdm_django_mapnik.ohdm.tags2mapnik import (cleanup_tags, fill_osm_object,
                                                 get_z_order, is_road)
from ohdm_django_mapnik.ohdm.utily import delete_last_terminal_line

from .models import (OhdmGeoobjectWay, PlanetOsmLine, PlanetOsmPoint,
                     PlanetOsmPolygon, PlanetOsmRoads)


class Ohdm2Mapnik:
    """
    convert ohdm database schema to mapnik readable Osm2pgsql schema

    -> https://wiki.openstreetmap.org/wiki/Osm2pgsql/schema
    """

    def __init__(self, chunk_size: int = 10000):
        """
        setup Ohdm2Mapnik class
        
        Keyword Arguments:
            chunk_size {int} -- how many entries will be load at once from database (default: {1000000})
        """
        self.chunk_size: int = chunk_size

        self.point_cache: List[PlanetOsmPoint] = []
        self.line_cache: List[PlanetOsmLine] = []
        self.road_cache: List[PlanetOsmRoads] = []
        self.polygon_cache: List[PlanetOsmPolygon] = []

        self.point_counter: int = 0
        self.line_counter: int = 0
        self.polygon_counter: int = 0

        # estimate total amount ob mapnik objects
        self.total_rows: int = 0

        # process start time
        self.start_time: float = 0

    def display_process_time(self):
        """
        display process time
        """

        row: int = (
            PlanetOsmLine.objects.all().count()
            + PlanetOsmPoint.objects.all().count()
            + PlanetOsmPolygon.objects.all().count()
        )

        process_time: float = time.time() - self.start_time
        percent: float = row / self.total_rows * 100

        if process_time <= 360:  # 6 minutes
            print(
                "--- {} rows of {} ({:.3f}%) in {:4.3f} seconds ---".format(
                    row, self.total_rows, percent, process_time
                )
            )
        elif process_time <= 7200:  # 120 minutes
            print(
                "--- {} rows of {} ({:.3f}%) in {:4.3f} minutes ---".format(
                    row, self.total_rows, percent, process_time / 60
                )
            )
        else:
            print(
                "--- {} rows of {} ({:.3f}%) in {:4.3f} hours ---".format(
                    row, self.total_rows, percent, process_time / 360
                )
            )

    def show_status(self):
        if (self.point_counter + self.line_counter + self.point_counter) % 10000 == 0:
            delete_last_terminal_line()
            print(
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
        print("saving cache ...")
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
        delete_last_terminal_line()

    def update_polygons(self):
        print("Make invalid polygons valid!")
        make_polygon_valid()
        print("Set way_area for all polygons!")
        set_polygon_way_area()

    def generate_sql_query(
        self, geo_type: str, offset: int = 0, count: bool = False
    ) -> str:
        """
        Generate SQL Query to fetch the request geo objects
        
        Arguments:
            offset {int} -- geo_type as string like point, line or polygon
            offset {int} -- query offset (default: {0})
            count {bool} -- if true, create a counting query (default: {False})
        
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

        if count:
            return """
                SELECT 
                    COUNT({0}s.id)
                FROM {2}.{0}s
                INNER JOIN {2}.geoobject_geometry ON {0}s.id=geoobject_geometry.id_target
                INNER JOIN {2}.geoobject ON geoobject_geometry.id_geoobject_source=geoobject.id
                INNER JOIN {2}.classification ON geoobject_geometry.classification_id=classification.id
                WHERE {1};
            """.format(
                geo_type, where_statement, env.str("OHDM_SCHEMA")
            )

        return """
                SELECT 
                    {0}s.id as way_id,
                    geoobject_geometry.id_geoobject_source as geoobject_id,
                    geoobject.name,
                    geoobject_geometry.role,
                    classification.class as classification_class,
	                classification.subclassname as classification_subclassname,
                    geoobject_geometry.tags,
                    geoobject_geometry.valid_since,
                    geoobject_geometry.valid_until,
                    {0}s.{0} as way
                FROM {4}.{0}s
                INNER JOIN {4}.geoobject_geometry ON {0}s.id=geoobject_geometry.id_target
                INNER JOIN {4}.geoobject ON geoobject_geometry.id_geoobject_source=geoobject.id
                INNER JOIN {4}.classification ON geoobject_geometry.classification_id=classification.id
                WHERE {3}
                LIMIT {1} OFFSET {2};
            """.format(
            geo_type, self.chunk_size, offset, where_statement, env.str("OHDM_SCHEMA"),
        )

    def count_rows(self, geo_type: str) -> int:
        """
        Count OHDM points, lines & polygons objects

        Keyword Arguments:
            geo_type {str} -- set geotype like point, line or polygon

        Returns:
            int -- counted rows
        """

        with connections["ohdm"].cursor() as cursor:

            cursor.execute(self.generate_sql_query(geo_type=geo_type, count=True))
            return cursor.fetchone()[0]

    def convert_points(self, offset: int, geometry: str):

        ohdm_object: OhdmGeoobjectWay
        for ohdm_object in OhdmGeoobjectWay.objects.using("ohdm").raw(
            self.generate_sql_query(geo_type=geometry, offset=offset)
        ):
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

            self.point_counter += 1
            self.show_status()
            self.check_cache_save()

    def convert_lines(self, offset: int, geometry: str):

        ohdm_object: OhdmGeoobjectWay
        for ohdm_object in OhdmGeoobjectWay.objects.using("ohdm").raw(
            self.generate_sql_query(geo_type=geometry, offset=offset)
        ):
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

            self.line_counter += 1
            self.show_status()
            self.check_cache_save()

    def convert_polygons(self, offset: int, geometry: str):

        ohdm_object: OhdmGeoobjectWay
        for ohdm_object in OhdmGeoobjectWay.objects.using("ohdm").raw(
            self.generate_sql_query(geo_type=geometry, offset=offset)
        ):
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

            self.polygon_counter += 1
            self.show_status()
            self.check_cache_save()

    def run(self):
        """
        convert ohdm database to mapnik readable tables
        """

        # calc total amount of rows
        self.total_rows = 0
        for geometry in OhdmGeoobjectWay.GEOMETRY_TYPE.TYPES:
            self.total_rows += self.count_rows(geo_type=geometry)

        print("Start converting of {} entries!".format(self.total_rows))

        # iterate through every ohdm entry
        for geometry in OhdmGeoobjectWay.GEOMETRY_TYPE.TYPES:
            print("Start to convert {} objects".format(geometry))

            rows: int = 0
            if geometry == OhdmGeoobjectWay.GEOMETRY_TYPE.POINT:
                rows = self.count_rows(geo_type=geometry)
                for row in range(0, rows, self.chunk_size):
                    self.convert_points(offset=row, geometry=geometry)
            elif geometry == OhdmGeoobjectWay.GEOMETRY_TYPE.LINE:
                rows = self.count_rows(geo_type=geometry)
                for row in range(0, rows, self.chunk_size):
                    self.convert_lines(offset=row, geometry=geometry)
            else:
                rows = self.count_rows(geo_type=geometry)
                for row in range(0, rows, self.chunk_size):
                    self.convert_polygons(offset=row, geometry=geometry)
                self.update_polygons()

            self.save_cache()
            print("{} is done!".format(geometry))

        print("All data are converted!")
