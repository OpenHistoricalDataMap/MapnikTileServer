from datetime import datetime
from typing import Dict

import pytest
from django.conf import settings
from django.test import RequestFactory

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
def tile_test_cases() -> Dict[str, dict]:
    """
    A dict of tile test cases
    
    Returns:
        Dict[str, dict] -- tile test cases
    """
    return {
        "Bremen": {
            "zoom": 17,
            "x": 68743,
            "y": 42652,
            "lat": "53.0742275131",
            "lon": "8.8082885742",
            "maxx": "980839.9469553815",
            "maxy": "6996739.821111893",
            "minx": "980534.198842241",
            "miny": "6996434.072998752",
            "osm_tile_url": "https://tile.openstreetmap.org/17/68743/42652.png",
            "osm_web_url": "https://www.openstreetmap.org/#map=17/53.07321/8.80942",
            "tile_png": "bremen-tile.png",
            "has_date_data": True,
        },
        "Sydney": {
            "zoom": 6,
            "x": 58,
            "y": 38,
            "lat": "-31.9521622380",
            "lon": "146.2500000000",
            "maxx": "16906647.66422842",
            "maxy": "-3757032.8142729816",
            "minx": "16280475.52851626",
            "miny": "-4383204.9499851465",
            "osm_tile_url": "https://a.tile.openstreetmap.org/6/58/38.png",
            "osm_web_url": "https://www.openstreetmap.org/#map=6/-31.952162238024954/146.25",
            "tile_png": "sydney-tile.png",
            "has_date_data": False,
        },
        "Antarctica": {
            "zoom": 7,
            "x": 74,
            "y": 123,
            "lat": "-83.6769430484",
            "lon": "28.1250000000",
            "maxx": "3443946.7464169012",
            "maxy": "-18472078.00350883",
            "minx": "3130860.678560819",
            "miny": "-18785164.071364917",
            "osm_tile_url": "https://c.tile.openstreetmap.org/7/74/123.png",
            "osm_web_url": "https://www.openstreetmap.org/#map=6/-83.67694304841551/28.125",
            "tile_png": "antarctica-tile.png",
            "has_date_data": False,
        },
    }
