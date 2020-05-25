from datetime import datetime
from random import randrange
from tempfile import SpooledTemporaryFile
from typing import Dict

import pytest
from django.core.cache import cache
from django.utils import timezone
from mapnik import Box2d
from PIL import Image, ImageChops

from ohdm_django_mapnik.ohdm.clear_db import clear_mapnik_tables
from ohdm_django_mapnik.ohdm.exceptions import (
    CoordinateOutOfRange,
    RenderErrorNoDate,
    ZoomOutOfRange,
)
from ohdm_django_mapnik.ohdm.import_osm import run_import
from ohdm_django_mapnik.ohdm.tile import TileGenerator


def test_tile_generator_init():
    """test TileGenerator constructor"""
    # test valid zoom level
    for zoom in range(20):
        if not isinstance(TileGenerator(zoom=zoom, x_pixel=0, y_pixel=0), TileGenerator):
            raise AssertionError

    # test zoom level with invalid zoom level
    with pytest.raises(ZoomOutOfRange):
        TileGenerator(zoom=-1, x_pixel=0, y_pixel=0)
    with pytest.raises(ZoomOutOfRange):
        TileGenerator(zoom=20, x_pixel=0, y_pixel=0)

    # test x & y coordinate limit
    for zoom in range(20):
        max_coordinate: int = int(pow(2, zoom))
        # x to low
        with pytest.raises(CoordinateOutOfRange):
            TileGenerator(zoom=zoom, x_pixel=-1, y_pixel=0)
        # y to low
        with pytest.raises(CoordinateOutOfRange):
            TileGenerator(zoom=zoom, x_pixel=0, y_pixel=-1)
        # x to high
        with pytest.raises(CoordinateOutOfRange):
            TileGenerator(zoom=zoom, x_pixel=max_coordinate + 1, y_pixel=0)
        # y to high
        with pytest.raises(CoordinateOutOfRange):
            TileGenerator(zoom=zoom, x_pixel=0, y_pixel=max_coordinate + 1)

        # valid y & x
        if not isinstance(
            TileGenerator(zoom=zoom, x_pixel=max_coordinate, y_pixel=0), TileGenerator
        ):
            raise AssertionError
        if not isinstance(
            TileGenerator(zoom=zoom, x_pixel=0, y_pixel=max_coordinate), TileGenerator
        ):
            raise AssertionError


def test_from_px_to_lon(tile_test_cases: Dict[str, dict]):
    """
    test if method from_px_to_lon convert px & zoom to lon

    Arguments:
        tile_test_cases {Dict[str, dict]} -- tile test cases
    """
    for test_case in tile_test_cases:
        print("lon test for {}".format(test_case))
        lon: float = TileGenerator.from_px_to_lon(
            px=tile_test_cases[test_case]["x"], zoom=tile_test_cases[test_case]["zoom"],
        )
        if "{:0.10f}".format(lon) != tile_test_cases[test_case]["lon"]:
            raise AssertionError
        if not isinstance(lon, float):
            raise AssertionError


def test_from_py_to_lat(tile_test_cases: Dict[str, dict]):
    """
    test if method from_py_to_lat convert px & zoom to lat

    Arguments:
        tile_test_cases {Dict[str, dict]} -- tile test cases
    """
    for test_case in tile_test_cases:
        print("lat test for {}".format(test_case))
        lat: float = TileGenerator.from_py_to_lat(
            py=tile_test_cases[test_case]["y"], zoom=tile_test_cases[test_case]["zoom"],
        )
        if "{:0.10f}".format(lat) != tile_test_cases[test_case]["lat"]:
            raise AssertionError
        if not isinstance(lat, float):
            raise AssertionError


def test_get_bbox_test_cases(
    tile_generator: TileGenerator, tile_test_cases: Dict[str, dict]
):
    """
    test get_bbox for cases and all tiles between zoomlevel 0 to 10

    Arguments:
        tile_generator {TileGenerator} -- default TileGenerator
        tile_test_cases {Dict[str, dict]} -- tile test cases
    """
    # test special cases
    for test_case in tile_test_cases:
        tile_generator.zoom = tile_test_cases[test_case]["zoom"]
        tile_generator.x_pixel = tile_test_cases[test_case]["x"]
        tile_generator.y_pixel = tile_test_cases[test_case]["y"]
        box2d: Box2d = tile_generator.get_bbox()
        if not isinstance(box2d, Box2d):
            raise AssertionError
        if "{}".format(box2d.maxx) != tile_test_cases[test_case]["maxx"]:
            raise AssertionError
        if "{}".format(box2d.maxy) != tile_test_cases[test_case]["maxy"]:
            raise AssertionError
        if "{}".format(box2d.minx) != tile_test_cases[test_case]["minx"]:
            raise AssertionError
        if "{}".format(box2d.miny) != tile_test_cases[test_case]["miny"]:
            raise AssertionError


def test_get_bbox_zoom_0_10(tile_generator: TileGenerator):
    """
    test get_bbox for all tiles between zoomlevel 0 to 10

    Arguments:
        tile_generator {TileGenerator} -- default TileGenerator
    """
    # test all tiles for zoom level 0 to 10
    tile_generator.get_bbox()
    for zoom in range(10):
        tile_generator.zoom = zoom
        for x in range(int(pow(2, zoom))):
            for y in range(int(pow(2, zoom))):
                tile_generator.x_pixel = x
                tile_generator.y_pixel = y
                if not isinstance(tile_generator.get_bbox(), Box2d):
                    raise AssertionError


def test_get_bbox_random_zoom_10_20(tile_generator: TileGenerator):
    """
    test get_bbox for random 1000 tiles each zoom level

    Arguments:
        tile_generator {TileGenerator} -- default TileGenerator
    """
    for zoom in range(10, 20):
        tile_generator.zoom = zoom
        coordinate_limit: int = int(pow(2, zoom))
        for _ in range(100):
            x: int = randrange(coordinate_limit)
            for _ in range(100):
                y: int = randrange(coordinate_limit)
                tile_generator.x_pixel = x
                tile_generator.y_pixel = y
                if not isinstance(tile_generator.get_bbox(), Box2d):
                    raise AssertionError


def test_render_tile_without_data(
    tile_generator: TileGenerator, tile_test_cases: Dict[str, dict]
):
    """
    test render tiles for tile_test_cases without using ohdm test data

    Arguments:
        tile_generator {TileGenerator} -- default TileGenerator
    """
    # clear cache
    cache.clear()

    for test_case in tile_test_cases:
        print("test: {}".format(test_case))
        tile_generator.zoom = tile_test_cases[test_case]["zoom"]
        tile_generator.x_pixel = tile_test_cases[test_case]["x"]
        tile_generator.y_pixel = tile_test_cases[test_case]["y"]

        # generate new tile into a tmp file
        new_tile: SpooledTemporaryFile = SpooledTemporaryFile()
        new_tile.write(tile_generator.render_tile())
        new_tile.seek(0)

        # open new tile as image
        new_tile_image: Image = Image.open(new_tile)

        # check if the tile is a PNG file
        if new_tile_image.format != "PNG":
            raise AssertionError

        # monochrome & resize images to better compare them
        reference_tile = Image.open(
            "/app/compose/local/django/test_tile/{}".format(
                tile_test_cases[test_case]["tile_png"]
            )
        )

        if ImageChops.difference(reference_tile, new_tile_image).getbbox() is not None:
            raise AssertionError


@pytest.mark.django_db(transaction=True, reset_sequences=True)
def test_render_tile_with_data(
    tile_generator: TileGenerator, tile_test_cases: Dict[str, dict]
):
    """
    test render tiles for tile_test_cases with using ohdm test data

    Arguments:
        tile_generator {TileGenerator} -- default TileGenerator
    """
    # cleanup data
    clear_mapnik_tables()

    # fill database
    run_import(
        file_path="/niue-latest.osm.pbf", db_cache_size=10000, cache2file=False,
    )

    tile_generator.request_date = timezone.now()

    for test_case in tile_test_cases:
        # contine if test case has not test data
        if not tile_test_cases[test_case]["has_date_data"]:
            continue

        print("test: {}".format(test_case))
        tile_generator.zoom = tile_test_cases[test_case]["zoom"]
        tile_generator.x_pixel = tile_test_cases[test_case]["x"]
        tile_generator.y_pixel = tile_test_cases[test_case]["y"]

        # generate new tile into a tmp file
        new_tile: SpooledTemporaryFile = SpooledTemporaryFile()
        new_tile.write(tile_generator.render_tile())
        new_tile.seek(0)

        # open new tile as image
        new_tile_image: Image = Image.open(new_tile)

        # check if the tile is a PNG file
        if new_tile_image.format != "PNG":
            raise AssertionError

        # monochrome & resize images to better compare them
        reference_tile = Image.open(
            "/app/compose/local/django/test_tile/{}".format(
                tile_test_cases[test_case]["tile_png"]
            )
        )

        diff: bool = ImageChops.difference(
            reference_tile, new_tile_image
        ).getbbox() is None

    # cleanup data
    clear_mapnik_tables()


def test_without_date():
    tile_generator: TileGenerator = TileGenerator(
        zoom=0, x_pixel=0, y_pixel=0, use_cache=False
    )

    with pytest.raises(RenderErrorNoDate):
        tile_generator.render_tile()
