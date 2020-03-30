import time
from datetime import datetime
from multiprocessing.pool import ThreadPool
from typing import Any, List

from config.settings.base import env
from django.db import connections

from .models import (
    OhdmGeoobjectWay,
    PlanetOsmLine,
    PlanetOsmPoint,
    PlanetOsmPolygon,
    PlanetOsmRoads,
    TileCache,
)


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

        # https://github.com/openstreetmap/osm2pgsql/blob/706f3a0a4696260c5b4a58950483d48967fd58ae/style.lua#L109
        self.zordering_tags: dict = {}
        self.zordering_tags["railway"] = {}
        self.zordering_tags["railway"]["0"] = tuple((5, 1))
        self.zordering_tags["boundary"] = {}
        self.zordering_tags["boundary"]["administrative"] = tuple((0, 1))
        self.zordering_tags["bridge"] = {}
        self.zordering_tags["bridge"]["yes"] = tuple((10, 0))
        self.zordering_tags["bridge"]["true"] = tuple((10, 0))
        self.zordering_tags["bridge"]["1"] = tuple((10, 0))
        self.zordering_tags["tunnel"] = {}
        self.zordering_tags["tunnel"]["yes"] = tuple((-10, 0))
        self.zordering_tags["tunnel"]["true"] = tuple((-10, 0))
        self.zordering_tags["tunnel"]["1"] = tuple((-10, 0))
        self.zordering_tags["highway"] = {}
        self.zordering_tags["highway"]["minor"] = tuple((3, 0))
        self.zordering_tags["highway"]["road"] = tuple((3, 0))
        self.zordering_tags["highway"]["unclassified"] = tuple((3, 0))
        self.zordering_tags["highway"]["residential"] = tuple((3, 0))
        self.zordering_tags["highway"]["tertiary_link"] = tuple((4, 0))
        self.zordering_tags["highway"]["tertiary"] = tuple((4, 0))
        self.zordering_tags["highway"]["secondary_link"] = tuple((6, 1))
        self.zordering_tags["highway"]["secondary"] = tuple((6, 1))
        self.zordering_tags["highway"]["primary_link"] = tuple((7, 1))
        self.zordering_tags["highway"]["primary"] = tuple((7, 1))
        self.zordering_tags["highway"]["trunk_link"] = tuple((8, 1))
        self.zordering_tags["highway"]["trunk"] = tuple((8, 1))
        self.zordering_tags["highway"]["motorway_link"] = tuple((9, 1))
        self.zordering_tags["highway"]["motorway"] = tuple((9, 1))

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

        print(
            "--- {} objects saved into database --- ".format(len(planet_object_cache))
        )

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
            geo_type,
            self.sql_chunk_size,
            offset,
            where_statement,
            env.str("OHDM_SCHEMA"),
        )

    def create_planet_object(
        self,
        name: str,
        geoobject: int,
        tags: Any,
        valid_since: datetime,
        valid_until: datetime,
        way: Any,
        geo_type: str,
    ) -> Any:
        """
        create unsaved planet object like PlanetOsmLine, PlanetOsmPoint or PlanetOsmPolygon
        
        Arguments:
            name {str} -- object name
            geoobject {int} -- geoobject id as int
            tags {Any} -- hstore tags
            valid_since {datetime} -- valid since as date
            valid_until {datetime} -- valid until as date
            way {Any} -- geoobject
            geo_type {str} -- OhdmGeoobjectWay.GEOMETRY_TYPE
        
        Returns:
            Any -- unsaved planet object
        """

        if geo_type == OhdmGeoobjectWay.GEOMETRY_TYPE.POINT:
            return PlanetOsmPoint(
                name=name,
                geoobject=geoobject,
                tags=tags,
                valid_since=valid_since,
                valid_until=valid_until,
                way=way,
            )
        elif geo_type == OhdmGeoobjectWay.GEOMETRY_TYPE.LINE:
            return PlanetOsmLine(
                name=name,
                geoobject=geoobject,
                tags=tags,
                valid_since=valid_since,
                valid_until=valid_until,
                way=way,
            )

        planet_object: PlanetOsmPolygon = PlanetOsmPolygon(
            name=name,
            geoobject=geoobject,
            tags=tags,
            valid_since=valid_since,
            valid_until=valid_until,
            way=way,
        )

        # add way_area, the area of the polygon
        # https://wiki.openstreetmap.org/wiki/Osm2pgsql/Key:way_area
        planet_object.way_area = planet_object.way.area

        return planet_object

    def convert(self, offset: int):
        """
        Convert OHDM Database into mapnik readable schema

        it will read all entries of the current object type beginning by
        range_begin and a limit of self.sql_chunk_size
        
        Arguments:
            offset {int} -- sql query offset
        """
        planet_object_cache: List[Any] = []
        planet_roads_cache: List[PlanetOsmRoads] = []

        for ohdm_object in OhdmGeoobjectWay.objects.using("ohdm").raw(
            self.generate_sql_query(geo_type=self.geo_type, offset=offset)
        ):
            planet_object: Any = self.create_planet_object(
                name=ohdm_object.name,
                geoobject=ohdm_object.geoobject_id,
                tags=ohdm_object.tags,
                valid_since=ohdm_object.valid_since,
                valid_until=ohdm_object.valid_until,
                way=ohdm_object.way,
                geo_type=self.geo_type,
            )

            # check if way is a valid geo object
            # if not planet_object.way.valid:
            #     print(
            #         "{} has invalid geometry -> {}".format(
            #             planet_object.name, planet_object.way.valid_reason
            #         )
            #     )
            #     continue

            # set classification attribute
            planet_object = self.add_classification(
                planet_object=planet_object,
                classification_class=ohdm_object.classification_class,
                classification_subclassname=ohdm_object.classification_subclassname,
            )

            # add z_order
            if self.geo_type != OhdmGeoobjectWay.GEOMETRY_TYPE.POINT:
                planet_objects = self.add_z_order(
                    planet_object=planet_object,
                    classification_class=ohdm_object.classification_class,
                    classification_subclassname=ohdm_object.classification_subclassname,
                )
                planet_object = planet_objects[0]

                if planet_objects[1]:
                    planet_roads_cache.append(planet_objects[1])

            try:
                planet_object.save()
            except:
                pass

            # planet_object_cache.append(planet_object)

        # self.save_planet_object_cache(planet_object_cache=planet_object_cache)
        PlanetOsmRoads.objects.bulk_create(planet_roads_cache)
        self.display_process_time()

    def add_classification(
        self,
        planet_object: Any,
        classification_class: str,
        classification_subclassname: str,
    ) -> Any:
        """
        Add classification to planet object
        
        Arguments:
            planet_object {Any} -- PlanetOsmLine, PlanetOsmPoint, PlanetOsmPolygon or PlanetOsmRoads
            classification_class {str} -- classification key
            classification_subclassname {str} -- classification value
        
        Returns:
            Any -- given planet object with classification
        """

        # if classification_subclassname has no valid value -> return planet_object without edit
        # todo check if this it needed
        if classification_subclassname == "undefined":
            return planet_object

        try:
            if not getattr(planet_object, classification_class):
                setattr(
                    planet_object, classification_class, classification_subclassname,
                )
        except AttributeError:
            pass

        return planet_object

    def add_z_order(
        self,
        planet_object: PlanetOsmLine,
        classification_class: str,
        classification_subclassname: str,
    ):
        """
        add z_order 
        based on -> https://github.com/openstreetmap/osm2pgsql/blob/706f3a0a4696260c5b4a58950483d48967fd58ae/style.lua
        """

        z_order: int = 0
        add_roads: bool = False

        # Add the value of the layer key times 10 to z_order
        try:
            z_order += (
                self.zordering_tags[classification_class][classification_subclassname][
                    0
                ]
                * 10
            )
            if (
                self.zordering_tags[classification_class][classification_subclassname][
                    1
                ]
                == 1
            ):
                add_roads = True
        except KeyError:
            pass

        # Increase or decrease z_order based on the specific key/value combination as specified in zordering_tags
        if planet_object.tags:
            tags: List[str] = planet_object.tags.replace('\\"', "'").split('"')

            for x in range(1, len(tags), 4):
                try:
                    # convert tags to classification
                    planet_object = self.add_classification(
                        planet_object=planet_object,
                        classification_class=tags[x],
                        classification_subclassname=tags[x + 2],
                    )

                    # calc z_order level
                    z_order += self.zordering_tags[tags[x]][tags[x + 2]][0]
                    if self.zordering_tags[tags[x]][tags[x + 2]][1] == 1:
                        add_roads = True
                except KeyError:
                    pass

        if self.geo_type != OhdmGeoobjectWay.GEOMETRY_TYPE.LINE:
            planet_object.z_order = z_order

        if add_roads and self.geo_type == OhdmGeoobjectWay.GEOMETRY_TYPE.LINE:
            roads: PlanetOsmRoads = PlanetOsmRoads(
                name=planet_object.name,
                # geoobject=planet_object.geoobject_id,
                tags=planet_object.tags,
                valid_since=planet_object.valid_since,
                valid_until=planet_object.valid_until,
                way=planet_object.way,
                z_order=z_order,
            )

            roads = self.add_classification(
                planet_object=roads,
                classification_class=classification_class,
                classification_subclassname=classification_subclassname,
            )

            return planet_object, roads

        return planet_object, None

    def repair_table(self, table: str):
        """
        Use Postgis repair function to repair broken geoobjects
        
        Arguments:
            table {str} -- table to repair
        """
        with connections["ohdm"].cursor() as cursor:
            cursor.execute(
                """
            UPDATE {}
            SET way = ST_MakeValid(way)
            WHERE not ST_IsValid(way); 
            """.format(
                    table
                )
            )
            return cursor.fetchone()[0]

    def run(self, threads: int = 1):
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

            rows: int = 0
            if geometry == OhdmGeoobjectWay.GEOMETRY_TYPE.POINT:
                rows = self.count_rows(geo_type=geometry)
            elif geometry == OhdmGeoobjectWay.GEOMETRY_TYPE.LINE:
                rows = self.count_rows(geo_type=geometry)
            else:
                rows = self.count_rows(geo_type=geometry)

            work_ids: List[int] = []
            for row in range(0, rows, self.sql_chunk_size):
                work_ids.append(row)

            pool: ThreadPool = ThreadPool(threads * 2)
            pool.map(self.convert, work_ids)
            pool.close()
            pool.join()

            self.repair_table(table="planet_osm_point")
            self.repair_table(table="planet_osm_line")
            self.repair_table(table="planet_osm_polygon")
            self.repair_table(table="planet_osm_roads")

            print("{} is done!".format(geometry))

        print("All data are converted!")
