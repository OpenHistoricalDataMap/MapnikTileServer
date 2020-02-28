import time
from multiprocessing.dummy import Pool as ThreadPool
from typing import Any, List

from django.db import connections

from config.settings.base import env

from .models import (OhdmGeoobjectWay, PlanetOsmLine, PlanetOsmPoint,
                     PlanetOsmPolygon, PlanetOsmRoads, TileCache)


class Ohdm2Mapnik:
    """
    convert ohdm database schema to mapnik readable Osm2pgsql schema

    -> https://wiki.openstreetmap.org/wiki/Osm2pgsql/schema
    """

    def __init__(self, sql_chunk_size: int = 1000000):
        """
        setup Ohdm2Mapnik class
        
        Keyword Arguments:
            sql_chunk_size {int} -- how many entries will be load at once from database (default: {1000000})
        """
        self.sql_chunk_size: int = sql_chunk_size

        # estimate total amount ob mapnik objects
        self.total_rows: int = 0

        # process start time
        self.start_time: float = 0

        # current geo_type
        self.geo_type: str = OhdmGeoobjectWay.GEOMETRY_TYPE.POINT

    def count_rows(self, geo_type: str) -> int:
        """
        Count OHDM points, lines & polygons objects

        Keyword Arguments:
            geo_type {str} -- set geotype like point, line or polygon

        Returns:
            int -- counted rows
        """

        with connections['ohdm'].cursor() as cursor:

            cursor.execute(self.generate_sql_query(geo_type=geo_type, count=True))
            return cursor.fetchone()[0]

    def drop_planet_tables(self):
        """
        Drop all data from mapnik tables and tile cache
        """
        PlanetOsmLine.objects.all().delete()
        PlanetOsmPoint.objects.all().delete()
        PlanetOsmPolygon.objects.all().delete()
        PlanetOsmRoads.objects.all().delete()
        TileCache.objects.all().delete()

    def save_planet_object_cache(self, planet_object_cache: List[Any]):
        """
        save planet_object_cache to database
        """

        if self.geo_type == OhdmGeoobjectWay.GEOMETRY_TYPE.POINT:
            PlanetOsmPoint.objects.bulk_create(planet_object_cache)
        elif self.geo_type == OhdmGeoobjectWay.GEOMETRY_TYPE.LINE:
            PlanetOsmLine.objects.bulk_create(planet_object_cache)
        else:
            PlanetOsmPolygon.objects.bulk_create(planet_object_cache)

        print("--- {} objects saved into database --- ".format(len(planet_object_cache)))

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

    def generate_sql_query(self, geo_type: str, offset: int = 0, count: bool = False) -> str:
        """
        Generate SQL Query to fetch the request geo objects
        
        Arguments:
            offset {int} -- geo_type as string like point, line or polygon
            offset {int} -- query offset (default: {0})
            count {bool} -- if true, create a counting query (default: {False})
        
        Returns:
            str -- SQL query as string
        """

        if geo_type == OhdmGeoobjectWay.GEOMETRY_TYPE.POINT:
            where_statement: str = "geoobject_geometry.type_target = 0 or geoobject_geometry.type_target = 1"
        elif geo_type == OhdmGeoobjectWay.GEOMETRY_TYPE.LINE:
            where_statement: str = "geoobject_geometry.type_target = 2"
        else:
            where_statement: str = "geoobject_geometry.type_target = 3"

        if count:
            return """
                SELECT 
                    COUNT({0}s.id)
                FROM {2}.{0}s
                INNER JOIN {2}.geoobject_geometry ON {0}s.id=geoobject_geometry.id_target
                INNER JOIN {2}.geoobject ON geoobject_geometry.id_geoobject_source=geoobject.id
                INNER JOIN {2}.classification ON geoobject_geometry.classification_id=classification.id
                WHERE {1};
            """.format(geo_type, where_statement, env.str("OHDM_SCHEMA"))

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
            """.format(geo_type, self.sql_chunk_size, offset, where_statement, env.str("OHDM_SCHEMA"))

    def convert(self, offset: int):
        """
        Convert OHDM Database into mapnik readable schema

        it will read all entries of the current object type beginning by
        range_begin and a limit of self.sql_chunk_size
        
        Arguments:
            offset {int} -- sql query offset
        """
        planet_object_cache: List[Any] = []

        for ohdm_object in OhdmGeoobjectWay.objects.using('ohdm').raw(
            self.generate_sql_query(geo_type=self.geo_type ,offset=offset)
        ):
            if self.geo_type == OhdmGeoobjectWay.GEOMETRY_TYPE.POINT:
                planet_object: Any = PlanetOsmPoint(
                    name=ohdm_object.name,
                    geoobject=ohdm_object.geoobject_id,
                    tags=ohdm_object.tags,
                    valid_since=ohdm_object.valid_since,
                    valid_until=ohdm_object.valid_until,
                    way=ohdm_object.way
                )
            elif self.geo_type == OhdmGeoobjectWay.GEOMETRY_TYPE.LINE:
                planet_object: Any = PlanetOsmLine(
                    name=ohdm_object.name,
                    geoobject=ohdm_object.geoobject_id,
                    tags=ohdm_object.tags,
                    valid_since=ohdm_object.valid_since,
                    valid_until=ohdm_object.valid_until,
                    way=ohdm_object.way
                )
            else:
                planet_object: Any = PlanetOsmPolygon(
                    name=ohdm_object.name,
                    geoobject=ohdm_object.geoobject_id,
                    tags=ohdm_object.tags,
                    valid_since=ohdm_object.valid_since,
                    valid_until=ohdm_object.valid_until,
                    way=ohdm_object.way
                )

            # set classification attribute
            if not ohdm_object.classification_subclassname == "undefined":
                try:
                    setattr(
                        planet_object, ohdm_object.classification_class, ohdm_object.classification_subclassname,
                    )
                except AttributeError:
                    print(
                        "{} has no attribute {}!".format(
                            type(planet_object), ohdm_object.classification_class,
                        )
                    )

            # check if way is a valid geo object
            if not planet_object.way.valid:
                print("{} has invalid geometry -> {}".format(
                    planet_object.name,
                    planet_object.way.valid_reason
                ))
            else:
                planet_object_cache.append(planet_object)

        self.save_planet_object_cache(planet_object_cache=planet_object_cache)
        self.display_process_time()

    def run(self, threads: int = 4):
        """
        convert ohdm database to mapnik readable tables
        
        Keyword Arguments:
            threads {int} -- how many threads should use for processing (default: number of CPU cores of host system)
        """
        self.start_time = time.time()

        print("Delete old mapnik tables!")
        self.drop_planet_tables()

        # calc total amount of rows
        self.total_rows = 0
        for geometry in OhdmGeoobjectWay.GEOMETRY_TYPE.TYPES:
            self.total_rows += self.count_rows(geo_type=geometry)
        
        print("Start converting of {} entries!".format(self.total_rows))

        # iterate through every ohdm entry
        for geometry in OhdmGeoobjectWay.GEOMETRY_TYPE.TYPES:
            print("Start to convert {} objects".format(geometry))
            self.geo_type = geometry

            if geometry == OhdmGeoobjectWay.GEOMETRY_TYPE.POINT:
                rows: int = self.count_rows(geo_type=geometry)
            elif geometry == OhdmGeoobjectWay.GEOMETRY_TYPE.LINE:
                rows: int = self.count_rows(geo_type=geometry)
            else:
                rows: int = self.count_rows(geo_type=geometry)

            work_ids: List[int] = []
            for row in range(0, rows, self.sql_chunk_size):
                work_ids.append(row)

            pool: ThreadPool = ThreadPool(threads * 2)
            pool.map(self.convert, work_ids)
            pool.close()
            pool.join()

            print("{} is done!".format(geometry))

        print("All data are converted!")
