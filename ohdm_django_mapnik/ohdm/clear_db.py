from .models import (
    DiffImportFiles,
    PlanetOsmLine,
    PlanetOsmNodes,
    PlanetOsmPoint,
    PlanetOsmPolygon,
    PlanetOsmRels,
    PlanetOsmRoads,
    PlanetOsmWays,
    TileCache,
)


def clear_rel_tables():
    """
    Clear all relation data
    """
    print("clear relation data")
    PlanetOsmNodes.objects.all().delete()
    PlanetOsmRels.objects.all().delete()
    PlanetOsmWays.objects.all().delete()

    DiffImportFiles.objects.all().delete()


def clear_mapnik_tables():
    """
    Clear all mapnik (osm2pgsql) data & tile cache
    """
    print("clear mapnik data & cache")

    PlanetOsmLine.objects.all().delete()
    PlanetOsmPoint.objects.all().delete()
    PlanetOsmPolygon.objects.all().delete()
    PlanetOsmRoads.objects.all().delete()
    TileCache.objects.all().delete()
