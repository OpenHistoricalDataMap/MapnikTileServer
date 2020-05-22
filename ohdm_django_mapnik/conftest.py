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
