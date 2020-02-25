from typing import Any, List, Optional, Tuple

from .models import (
    OhdmGeoobject,
    OhdmGeoobjectGeometry,
    PlanetOsmLine,
    PlanetOsmPoint,
    PlanetOsmPolygon,
    PlanetOsmRoads,
)


def drop_planet_tables():
    PlanetOsmLine.objects.all().delete()
    PlanetOsmPoint.objects.all().delete()
    PlanetOsmPolygon.objects.all().delete()
    PlanetOsmRoads.objects.all().delete()


def ohdm2mapnik():
    """
    Drop old data from:
        - TileCache
        - PlanetOsmLine
        - PlanetOsmPoint
        - PlanetOsmPolygon
        - PlanetOsmRoads

    Fill the planet tabels from ohdm data.
    """

    drop_planet_tables()

    for geoobject in OhdmGeoobject.objects.filter(name__isnull=True):
        for geoobject_geometry in OhdmGeoobjectGeometry.objects.filter(
            id_geoobject_source=geoobject
        ):
            planet_object: Optional[Any] = geoobject_geometry.get_planet_object()

            if not planet_object:
                print(
                    "{} {} is no valid geometry object!".format(
                        geoobject.id, geoobject.name
                    )
                )
                continue

            planet_object.name = geoobject.name
            planet_object.geoobject = geoobject

            try:
                setattr(
                    planet_object,
                    geoobject_geometry.classification_id.class_field,
                    geoobject_geometry.classification_id.subclassname,
                )
            except AttributeError:
                print(
                    "{} has no attribute {}!".format(
                        type(planet_object),
                        geoobject_geometry.classification_id.class_field,
                    )
                )

            planet_object.save()
            print(planet_object.id)

    for geoobject in OhdmGeoobject.objects.filter(name__isnull=False):

        # get all OhdmGeoobjectGeometry object based on geoobject
        geoobjects_geometry: List[
            OhdmGeoobjectGeometry
        ] = OhdmGeoobjectGeometry.objects.filter(id_geoobject_source=geoobject)

        # continue to next geoobject when no OhdmGeoobjectGeometry exists
        if len(geoobjects_geometry) < 1:
            print(
                "{} {} does not have any GeoobjectGeometry entries!".format(
                    geoobject.id, geoobject.name
                )
            )
            continue

        # get planet_object like PlanetOsmPoint, PlanetOsmLine, PlanetOsmPolygon
        planet_object: Optional[Any] = geoobjects_geometry[0].get_planet_object()

        # continue if planet_object not exists
        if not planet_object:
            print(
                "{} {} is no valid geometry object!".format(
                    geoobject.id, geoobject.name
                )
            )
            continue

        # fill planet_object with base values
        planet_object.name = geoobject.name
        planet_object.geoobject = geoobject

        for geoobject_geometry in geoobjects_geometry:
            try:
                setattr(
                    planet_object,
                    geoobject_geometry.classification_id.class_field,
                    geoobject_geometry.classification_id.subclassname,
                )
            except AttributeError:
                print(
                    "{} has no attribute {}!".format(
                        type(planet_object),
                        geoobject_geometry.classification_id.class_field,
                    )
                )

        planet_object.save()
        print("{} saved!".format(planet_object))
