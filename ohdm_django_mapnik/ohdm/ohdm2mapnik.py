import time
from multiprocessing.dummy import Pool as ThreadPool
from typing import Any, List, Optional, Tuple

from .models import (OhdmClassification, OhdmGeoobjectWay, OhdmLines,
                     OhdmPoints, OhdmPolygons, PlanetOsmLine, PlanetOsmPoint,
                     PlanetOsmPolygon, PlanetOsmRoads, TileCache)


class OhdmClassificationCache:
    """
    Cache all OhdmClassification entries for fast converting ohdm table to mapnik
    """

    def __init__(self):
        self.classifications: List[
            OhdmClassification
        ] = OhdmClassification.objects.all()

    def get_value(self, classification_id: int) -> Tuple[str, Optional[str]]:
        """
        Get OHDM classifications based on the classifications_id
        
        Arguments:
            classification_id {int} -- the request classification
        
        Returns:
            Tuple[str, Optional[str]] -- class, subclassname
        """
        return self.classifications[classification_id].get_value()


class Ohdm2Mapnik:
    """
    convert ohdm database schema to mapnik readable Osm2pgsql schema

    -> https://wiki.openstreetmap.org/wiki/Osm2pgsql/schema
    """

    def __init__(self, sql_chunk_size: int = 1000000):
        """
        setup Ohdm2Mapnik class
        
        Keyword Arguments:
            sql_chunk_size {int} -- how many entries will be load at once from database (default: {100000})
        """
        self.sql_chunk_size: int = sql_chunk_size

        # OhdmClassificationCache
        self.classification_cache: OhdmClassificationCache = OhdmClassificationCache()

        # estimate total amount ob mapnik objects
        self.estimate_total_rows: int = 0

        # process start time
        self.start_time: float = 0

        # current geo_type
        self.geo_type: str = OhdmGeoobjectWay.GEOMETRY_TYPE.POINT

    def drop_planet_tables(self):
        """
        Drop all data from mapnik tables and tile cache
        """
        PlanetOsmLine.objects.all().delete()
        PlanetOsmPoint.objects.all().delete()
        PlanetOsmPolygon.objects.all().delete()
        PlanetOsmRoads.objects.all().delete()
        TileCache.objects.all().delete()

    def set_classification(self, planet_object: Any, classification_id: int) -> Any:
        """Add classification to planet_object
        
        Arguments:
            planet_object {Any} -- PlanetOsmLine, PlanetOsmPoint or PlanetOsmPolygon
            classification_id {int} -- id of OhdmClassification table
        
        Returns:
            Any -- given planet_object with added classification
        """

        classification: Tuple[str, Optional[str]] = self.classification_cache.get_value(
            classification_id=classification_id
        )

        try:
            setattr(
                planet_object, classification[0], classification[1],
            )
        except AttributeError:
            print(
                "{} has no attribute {}!".format(
                    type(planet_object), classification[0],
                )
            )
        return planet_object

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
        percent: float = row / self.estimate_total_rows * 100

        if process_time <= 360:  # 6 minutes
            print(
                "--- {} rows of {} ({:.3f}%) in {:4.3f} seconds ---".format(
                    row, self.estimate_total_rows, percent, process_time
                )
            )
        elif process_time <= 7200:  # 120 minutes
            print(
                "--- {} rows of {} ({:.3f}%) in {:4.3f} minutes ---".format(
                    row, self.estimate_total_rows, percent, process_time / 60
                )
            )
        else:
            print(
                "--- {} rows of {} ({:.3f}%) in {:4.3f} hours ---".format(
                    row, self.estimate_total_rows, percent, process_time / 360
                )
            )

    def generate_sql_query(self, offset: int) -> str:
        """
        Generate SQL Query to fetch the request geo objects
        
        Arguments:
            offset {int} -- query offset
        
        Returns:
            str -- SQL query as string
        """

        if self.geo_type == OhdmGeoobjectWay.GEOMETRY_TYPE.POINT:
            where_statement: str = "geoobject_geometry.type_target = 0 or geoobject_geometry.type_target = 1"
        elif self.geo_type == OhdmGeoobjectWay.GEOMETRY_TYPE.LINE:
            where_statement: str = "geoobject_geometry.type_target = 2"
        else:
            where_statement: str = "geoobject_geometry.type_target = 3"

        return """
                SELECT 
                    {0}s.id as way_id,
                    geoobject_geometry.id_geoobject_source as geoobject_id,
                    geoobject.name,
                    geoobject_geometry.role,
                    geoobject_geometry.classification_id,
                    geoobject_geometry.tags,
                    geoobject_geometry.valid_since,
                    geoobject_geometry.valid_until,
                    {0}s.{0} as way
                FROM public.{0}s
                INNER JOIN public.geoobject_geometry ON {0}s.id=geoobject_geometry.id_target
                INNER JOIN public.geoobject ON geoobject_geometry.id_geoobject_source=geoobject.id
                WHERE {3}
                GROUP BY way_id, geoobject_id, name, role, classification_id, tags, valid_since, valid_until, way
                LIMIT {1} OFFSET {2};
            """.format(self.geo_type, self.sql_chunk_size, offset, where_statement)

    def convert(self, offset: int):
        """
        Convert OHDM Database into mapnik readable schema

        it will read all entries of the current object type beginning by
        range_begin and a limit of self.sql_chunk_size
        
        Arguments:
            offset {int} -- sql query offset
        """
        planet_object_cache: List[Any] = []

        for ohdm_object in OhdmGeoobjectWay.objects.raw(
            self.generate_sql_query(offset=offset)
        ):
            if self.geo_type == OhdmGeoobjectWay.GEOMETRY_TYPE.POINT:
                planet_object: Any = PlanetOsmPoint(
                    name=ohdm_object.name,
                    # geoobject=ohdm_object.geoobject_id,
                    tags=ohdm_object.tags,
                    valid_since=ohdm_object.valid_since,
                    valid_until=ohdm_object.valid_until,
                    way=ohdm_object.way
                )
            elif self.geo_type == OhdmGeoobjectWay.GEOMETRY_TYPE.LINE:
                planet_object: Any = PlanetOsmLine(
                    name=ohdm_object.name,
                    # geoobject=ohdm_object.geoobject_id,
                    tags=ohdm_object.tags,
                    valid_since=ohdm_object.valid_since,
                    valid_until=ohdm_object.valid_until,
                    way=ohdm_object.way
                )
            else:
                planet_object: Any = PlanetOsmPolygon(
                    name=ohdm_object.name,
                    # geoobject=ohdm_object.geoobject_id,
                    tags=ohdm_object.tags,
                    valid_since=ohdm_object.valid_since,
                    valid_until=ohdm_object.valid_until,
                    way=ohdm_object.way
                )

            planet_object = self.set_classification(
                            planet_object=planet_object,
                            classification_id=ohdm_object.classification_id,
                        )

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

        # calc estimate amount of rows
        self.estimate_total_rows = (
            OhdmLines.objects.all().count()
            + OhdmPolygons.objects.all().count()
            + OhdmPoints.objects.all().count()
        )

        print("Start converting of {} entries!".format(self.estimate_total_rows))

        # iterate through every ohdm entry
        for geometry in OhdmGeoobjectWay.GEOMETRY_TYPE.TYPES:
            print("Start to convert {} objects".format(geometry))
            self.geo_type = geometry

            if geometry == OhdmGeoobjectWay.GEOMETRY_TYPE.POINT:
                rows: int = OhdmPoints.objects.all().count()
            elif geometry == OhdmGeoobjectWay.GEOMETRY_TYPE.LINE:
                rows: int = OhdmLines.objects.all().count()
            else:
                rows: int = OhdmPolygons.objects.all().count()

            work_ids: List[int] = []
            for row in range(0, rows, self.sql_chunk_size):
                work_ids.append(row)

            pool: ThreadPool = ThreadPool(threads * 2)
            pool.map(self.convert, work_ids)
            pool.close()
            pool.join()

            print("{} is done!".format(geometry))

        print("All data are converted!")
