from time import time

import pytest
from django.core.cache import cache

from ohdm_django_mapnik.ohdm.models import TileCache
from ohdm_django_mapnik.ohdm.tests.factories import (
    FinishTileCacheFactory,
    RunningTileCacheFactory,
)


@pytest.mark.django_db()
def test_get_cache_key():
    """
    test TileCache get_cache_key function
    """
    tile_cache: TileCache = FinishTileCacheFactory()
    assert tile_cache.get_cache_key() == "t{}".format(tile_cache.pk)


@pytest.mark.django_db()
def test_get_tile_from_cache_or_delete():
    """
    test TileCache get_tile_from_cache_or_delete function
    """
    # test waiting for tile producer is finish
    start_test: int = int(time())
    tc_running: TileCache = RunningTileCacheFactory()
    tc_running.get_tile_from_cache_or_delete()
    assert int(time()) < start_test + 10

    # test with no cache file
    tc_finish_no_cache: TileCache = FinishTileCacheFactory()
    assert tc_finish_no_cache.get_tile_from_cache_or_delete() is None

    # test with cache file
    tc_finish_cache: TileCache = FinishTileCacheFactory()
    tile: bytes = b"tile"
    cache.set(tc_finish_cache.get_cache_key(), tile)
    assert tc_finish_cache.get_tile_from_cache_or_delete() == tile
    cache.delete(tc_finish_cache.get_cache_key())


@pytest.mark.django_db()
def test_delete():
    """
    test TileCache delete function
    """
    # test without cache file
    tc_no_cache: TileCache = FinishTileCacheFactory()
    tc_no_cache.delete()
    assert cache.get(tc_no_cache.get_cache_key()) is None

    # test with cache file
    tc_cache: TileCache = FinishTileCacheFactory()
    cache.set(tc_cache.get_cache_key(), b"tile")
    tc_cache.delete()
    assert cache.get(tc_cache.get_cache_key()) is None
