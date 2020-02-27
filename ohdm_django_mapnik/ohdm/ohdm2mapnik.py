import multiprocessing
import time
from multiprocessing.dummy import Pool as ThreadPool
from typing import Any, List, Optional, Tuple

from ohdm_django_mapnik.ohdm.models import (
    OhdmClassification,
    OhdmLines,
    OhdmPoints,
    OhdmPolygons,
)

from .models import (
    OhdmGeoobject,
    OhdmGeoobjectGeometry,
    PlanetOsmLine,
    PlanetOsmPoint,
    PlanetOsmPolygon,
    PlanetOsmRoads,
    TileCache,
)


def drop_planet_tables():
    PlanetOsmLine.objects.all().delete()
    PlanetOsmPoint.objects.all().delete()
    PlanetOsmPolygon.objects.all().delete()
    PlanetOsmRoads.objects.all().delete()
    TileCache.objects.all().delete()


class OhdmClassificationCache:
    """
    Cache all OhdmClassification entries for fast converting ohdm table to mapnik
    """

    def __init__(self):
        self.classifications: List[
            OhdmClassification
        ] = OhdmClassification.objects.all()

    def get_value(self, classification_id: int) -> Tuple[str, Optional[str]]:
        return self.classifications[classification_id].get_value()


class Ohdm2Mapnik:
    """
    convert ohdm database schema to mapnik readable Osm2pgsql schema

    -> https://wiki.openstreetmap.org/wiki/Osm2pgsql/schema
    """

    def __init__(self, bulk_amount: int = 1000, sql_chunk_size: int = 1000):
        """
        setup Ohdm2Mapnik class
        
        Keyword Arguments:
            bulk_amount {int} -- how many new objects will be saved at once (default: {100000})
            sql_chunk_size {int} -- how many entries will be load at once from database (default: {100000})
        """
        self.bulk_amount: int = bulk_amount
        self.sql_chunk_size: int = sql_chunk_size

        # PlanetOsm object cache
        self.planet_points: List[PlanetOsmPoint] = []
        self.planet_line: List[PlanetOsmLine] = []
        self.planet_polygon: List[PlanetOsmPolygon] = []

        # OhdmClassificationCache
        self.classification_cache: OhdmClassificationCache = OhdmClassificationCache()

        # count how many rows converted
        self.row: int = 0

        # estimate total amount ob mapnik objects
        self.estimate_total_rows: int = 0

        # process start time
        self.start_time: float = 0

        # already added objects ids (useful to not add double objects)
        self.done_objects: List[int] = []

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

    def planet_object_to_cache(self, planet_object: Any):
        """add planet_object to cache
        
        Arguments:
            planet_object {Any} -- PlanetOsmLine, PlanetOsmPoint or PlanetOsmPolygon object witch should be saved
        """
        if isinstance(planet_object, PlanetOsmPoint):
            self.planet_points.append(planet_object)
        elif isinstance(planet_object, PlanetOsmLine):
            self.planet_line.append(planet_object)
        else:
            self.planet_polygon.append(planet_object)

    def save_planet_object_cache(self):
        """
        save planet_object_cache to database
        """
        PlanetOsmPoint.objects.bulk_create(self.planet_points)
        self.planet_points.clear()
        PlanetOsmLine.objects.bulk_create(self.planet_line)
        self.planet_line.clear()
        PlanetOsmPolygon.objects.bulk_create(self.planet_polygon)
        self.planet_polygon.clear()

        print("--- {} objects saved into database --- ".format(self.row))

    def display_process_time(self):
        """
        display process time
        """

        self.row = (
            PlanetOsmLine.objects.all().count()
            + PlanetOsmPoint.objects.all().count()
            + PlanetOsmPolygon.objects.all().count()
        )

        process_time: float = time.time() - self.start_time
        percent: float = self.row / self.estimate_total_rows * 100

        if process_time <= 360:  # 6 minutes
            print(
                "--- {} rows of {} ({:.3f}%) in {:4.3f} seconds ---".format(
                    self.row, self.estimate_total_rows, percent, process_time
                )
            )
        elif process_time <= 7200:  # 120 minutes
            print(
                "--- {} rows of {} ({:.3f}%) in {:4.3f} minutes ---".format(
                    self.row, self.estimate_total_rows, percent, process_time / 60
                )
            )
        else:
            print(
                "--- {} rows of {} ({:.3f}%) in {:4.3f} hours ---".format(
                    self.row, self.estimate_total_rows, percent, process_time / 360
                )
            )

    def count_row(self, planet_object: Any):
        """
        Count rows & saved planet_object_cache to database

        Arguments:
            planet_object {Any} -- PlanetOsmLine, PlanetOsmPoint or PlanetOsmPolygon object witch should be added to cache & db
        """
        # self.row += 1

        # self.planet_object_to_cache(planet_object=planet_object)
        planet_object.save()

        # if self.row % self.bulk_amount == 0:
        #     self.save_planet_object_cache()

        # print(self.row)

        # if self.row % 1000 == 0:
        #     self.display_process_time()

    def convert(self, range_begin: int):
        for geoobject in OhdmGeoobject.objects.all()[
            range_begin : range_begin + self.sql_chunk_size
        ]:
            if not geoobject.name:

                # load all geoobject_geometry for geoobject
                for geoobject_geometry in OhdmGeoobjectGeometry.objects.filter(
                    id_geoobject_source=geoobject
                ):
                    # jump already added objects
                    if geoobject_geometry.id in self.done_objects:
                        return

                    planet_object: Optional[
                        Any
                    ] = geoobject_geometry.get_planet_object()

                    # continue if planet_object not exists
                    if not planet_object:
                        print("{} is no valid geometry object!".format(geoobject.id))
                        return

                    planet_object.name = geoobject.name
                    planet_object.geoobject = geoobject

                    if (
                        OhdmGeoobjectGeometry.objects.filter(
                            id_target=geoobject_geometry.id_target,
                            type_target=geoobject_geometry.type_target,
                        ).count()
                        > 1
                    ):
                        for (
                            geoobject_geometry_sub
                        ) in OhdmGeoobjectGeometry.objects.filter(
                            id_target=geoobject_geometry.id_target,
                            type_target=geoobject_geometry.type_target,
                        ):
                            self.done_objects.append(geoobject_geometry_sub.id)
                            planet_object = self.set_classification(
                                planet_object=planet_object,
                                classification_id=geoobject_geometry_sub.classification_id,
                            )
                    else:
                        planet_object = self.set_classification(
                            planet_object=planet_object,
                            classification_id=geoobject_geometry.classification_id,
                        )

                    self.count_row(planet_object=planet_object)

            else:
                geoobjects_geometry: List[
                    OhdmGeoobjectGeometry
                ] = OhdmGeoobjectGeometry.objects.filter(id_geoobject_source=geoobject)

                # get planet_object like PlanetOsmPoint, PlanetOsmLine, PlanetOsmPolygon
                planet_object: Optional[Any] = geoobjects_geometry[
                    0
                ].get_planet_object()

                # continue if planet_object not exists
                if not planet_object:
                    print(
                        "{} {} is no valid geometry object!".format(
                            geoobject.id, geoobject.name
                        )
                    )
                    return

                # fill planet_object with base values
                planet_object.name = geoobject.name
                planet_object.geoobject = geoobject

                for geoobject_geometry in geoobjects_geometry:
                    planet_object = self.set_classification(
                        planet_object=planet_object,
                        classification_id=geoobject_geometry.classification_id,
                    )

                self.count_row(planet_object=planet_object)

        self.display_process_time()

    def run(self, threads: int = multiprocessing.cpu_count()):
        """
        convert ohdm database to mapnik readable tables
        
        Keyword Arguments:
            threads {int} -- how many threads should use for processing (default: number of CPU cores of host system)
        """
        self.start_time = time.time()

        self.done_objects.clear()

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
        rows: int = OhdmGeoobject.objects.all().count()
        work_ids: List[int] = []
        for row in range(0, rows, self.sql_chunk_size):
            work_ids.append(row)

        pool: ThreadPool = ThreadPool(threads)
        pool.map(self.convert, work_ids)
        pool.close()
        pool.join()

        # save last objects
        # self.save_planet_object_cache()
