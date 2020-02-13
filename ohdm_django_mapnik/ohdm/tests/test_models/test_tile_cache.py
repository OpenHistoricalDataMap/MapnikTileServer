import pytest

from ohdm_django_mapnik.ohdm.models import TileCache
from ohdm_django_mapnik.ohdm.tests.factories import TileCacheFactory


@pytest.mark.django_db()
def test_get_cache_key():
    """
    test TileCache get_cache_key function
    """
    tile_cache: TileCache = TileCacheFactory()
    assert tile_cache.get_cache_key() == "t{}".format(tile_cache.pk)
