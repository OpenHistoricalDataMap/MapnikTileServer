from django.core.cache import cache

from .models import (PlanetOsmLine, PlanetOsmNodes, PlanetOsmPoint,
                     PlanetOsmPolygon, PlanetOsmRels, PlanetOsmRoads,
                     PlanetOsmWays)


def clear_rel_tables():
    """
    Clear all relation data
    """
    print("clear relation data")
    PlanetOsmNodes.objects.all().delete()
    PlanetOsmRels.objects.all().delete()
    PlanetOsmWays.objects.all().delete()


def clear_mapnik_tables():
    """
    Clear all mapnik (osm2pgsql) data & tile cache
    """
    print("clear mapnik data & cache")

    # clear database
    PlanetOsmLine.objects.all().delete()
    PlanetOsmPoint.objects.all().delete()
    PlanetOsmPolygon.objects.all().delete()
    PlanetOsmRoads.objects.all().delete()

    # clear cache
    cache.clear()
