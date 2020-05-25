import pytest

from django.db import connection
from ohdm_django_mapnik.ohdm.clear_db import clear_mapnik_tables
from ohdm_django_mapnik.ohdm.import_osh import run_import as run_osh_import
from ohdm_django_mapnik.ohdm.import_osm import run_import as run_osm_import
from ohdm_django_mapnik.ohdm.models import (
    GeoobjectGeometry,
    OhdmGeoobjectLine,
    OhdmGeoobjectPoint,
    OhdmGeoobjectPolygon,
    PlanetOsmLine,
    PlanetOsmPoint,
    PlanetOsmPolygon,
    PlanetOsmRoads,
)
from ohdm_django_mapnik.ohdm.rel2pgsql import Rel2pgsql


@pytest.mark.django_db()
def test_import_osm():
    # fill database with osm importer
    run_osm_import(
        file_path="/niue-latest.osm.pbf", db_cache_size=10000, cache2file=False,
    )

    # count mapnik entries
    osm_point_count: int = PlanetOsmPoint.objects.all().count()
    osm_line_count: int = PlanetOsmLine.objects.all().count()
    osm_road_count: int = PlanetOsmRoads.objects.all().count()
    osm_polygon_count: int = PlanetOsmPolygon.objects.all().count()

    # check if there was added any mapnik entry
    assert osm_point_count > 0
    assert osm_line_count > 0
    assert osm_road_count > 0
    assert osm_polygon_count > 0


@pytest.mark.django_db()
def test_import_osh():
    # fill database with osh importer
    run_osh_import(
        file_path="/niue-latest.osm.pbf", db_cache_size=10000, cache2file=False,
    )

    # convert relations to mapnik tables
    rel2pgsql: Rel2pgsql = Rel2pgsql(chunk_size=10000)
    rel2pgsql.run_import()

    # count mapnik entries
    osh_point_count: int = PlanetOsmPoint.objects.all().count()
    osh_line_count: int = PlanetOsmLine.objects.all().count()
    osh_road_count: int = PlanetOsmRoads.objects.all().count()
    osh_polygon_count: int = PlanetOsmPolygon.objects.all().count()

    # check if there was added any mapnik entry
    assert osh_point_count > 0
    assert osh_line_count > 0
    assert osh_road_count > 0
    assert osh_polygon_count > 0
