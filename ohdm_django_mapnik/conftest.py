import csv
from datetime import datetime
from typing import Dict, List

import pytest
from django.conf import settings
from django.test import RequestFactory

from ohdm_django_mapnik.ohdm.models import (
    Classification,
    Geoobject,
    GeoobjectGeometry,
    Lines,
    Points,
    Polygons,
)
from ohdm_django_mapnik.ohdm.ohdm2mapnik import Ohdm2Mapnik
from ohdm_django_mapnik.ohdm.tile import TileGenerator


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def tile_generator() -> TileGenerator:
    return TileGenerator(
        zoom=0, x_pixel=0, y_pixel=0, request_date=datetime(2020, 1, 1), use_cache=False
    )


@pytest.fixture
def test_tile() -> Dict[str, dict]:
    """
    A dict with all values to tests a single tile

    Returns:
        Dict[str, dict] -- test tile data
    """
    return {
        "data": {
            "year": 2020,
            "month": 1,
            "day": 1,
            "zoom": 0,
            "x_pixel": 0,
            "y_pixel": 0,
        },
        "no-data-data": {"zoom": 0, "x_pixel": 0, "y_pixel": 0,},
        "cache": {
            "tile_hash": "e5e9e200cd28d88296ddd282d6ec0651",
            "cache_key": "2020-1-1-0-0-0",
        },
    }


@pytest.fixture
def tile_test_cases() -> Dict[str, dict]:
    """
    A dict of tile test cases

    Returns:
        Dict[str, dict] -- tile test cases
    """
    return {
        "Niue": {
            "zoom": 18,
            "x": 7341,
            "y": 145207,
            "lat": "-19.0504355920",
            "lon": "-169.9186706543",
            "maxx": "-18915107.019449715",
            "maxy": "-2160874.789621933",
            "minx": "-18915259.893506285",
            "miny": "-2161027.6636785036",
            "osm_tile_url": "https://tile.openstreetmap.org/18/7341/145207.png",
            "osm_web_url": "https://www.openstreetmap.org/#map=18/-19.0504355920/-169.9186706543",
            "tile_png": "niue-tile.png",
            "has_date_data": True,
        },
        "Sydney": {
            "zoom": 6,
            "x": 57,
            "y": 38,
            "lat": "-31.9521622380",
            "lon": "140.6250000000",
            "maxx": "16280475.52851626",
            "maxy": "-3757032.8142729816",
            "minx": "15654303.392804096",
            "miny": "-4383204.9499851465",
            "osm_tile_url": "https://a.tile.openstreetmap.org/6/57/38.png",
            "osm_web_url": "https://www.openstreetmap.org/#map=6/-31.952162238024954/146.25",
            "tile_png": "sydney-tile.png",
            "has_date_data": False,
        },
    }


@pytest.fixture
def ohdm2mapnik() -> Ohdm2Mapnik:
    # fill ohdm database

    # classification
    classifications: List[Classification] = list()
    with open("compose/production/django/test-data/classification.csv") as csvfile:
        for row in csv.reader(csvfile, delimiter=",", quotechar='"'):
            if len(row) == 3:
                classifications.append(
                    Classification(id=row[0], class_field=row[1], subclassname=row[2])
                )
    Classification.objects.bulk_create(classifications)

    # geoobject
    geoobjects: List[Geoobject] = list()
    with open("compose/production/django/test-data/geoobject.csv") as csvfile:
        for row in csv.reader(csvfile, delimiter=",", quotechar='"'):
            if len(row) == 3:
                geoobjects.append(
                    Geoobject(id=row[0], name=row[1], source_user_id=row[2])
                )
    Geoobject.objects.bulk_create(geoobjects)

    # geoobject_geometry
    geoobject_geometrys: List[GeoobjectGeometry] = list()
    with open("compose/production/django/test-data/geoobject_geometry.csv") as csvfile:
        for row in csv.reader(csvfile, delimiter=",", quotechar='"'):
            if len(row) == 12:
                geoobject_geometry: GeoobjectGeometry = GeoobjectGeometry(
                    id=row[0],
                    id_target=row[1],
                    type_target=row[2],
                    id_geoobject_source=row[3],
                    # role=row[4],
                    classification_id=row[5],
                    # tags=row[6],
                    valid_since=row[7],
                    valid_until=row[8],
                    valid_since_offset=row[9],
                    valid_until_offset=row[10],
                    source_user_id=row[11],
                )

                if row[4] != "NULL":
                    geoobject_geometry.role = row[4]
                if row[6] != "NULL":
                    geoobject_geometry.tags = row[6]

                geoobject_geometrys.append(geoobject_geometry)

    GeoobjectGeometry.objects.bulk_create(geoobject_geometrys)

    # points
    points: List[Points] = list()
    with open("compose/production/django/test-data/points.csv") as csvfile:
        for row in csv.reader(csvfile, delimiter=",", quotechar='"'):
            if len(row) == 3:
                points.append(Points(id=row[0], point=row[1], source_user_id=row[2]))
    Points.objects.bulk_create(points)

    # lines
    lines: List[Lines] = list()
    with open("compose/production/django/test-data/lines.csv") as csvfile:
        for row in csv.reader(csvfile, delimiter=",", quotechar='"'):
            if len(row) == 3:
                lines.append(Lines(id=row[0], line=row[1], source_user_id=row[2]))
    Lines.objects.bulk_create(lines)

    # polygons
    polygons: List[Polygons] = list()
    with open("compose/production/django/test-data/polygons.csv") as csvfile:
        for row in csv.reader(csvfile, delimiter=",", quotechar='"'):
            if len(row) == 3:
                polygons.append(
                    Polygons(id=row[0], polygon=row[1], source_user_id=row[2])
                )
    Polygons.objects.bulk_create(polygons)

    return Ohdm2Mapnik(ohdm_schema="public")
