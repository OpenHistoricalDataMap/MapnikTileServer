from typing import Dict, Optional

from config.settings.base import OSM_CARTO_STYLE_XML, env
from django.core.cache import cache
from ohdm_django_mapnik.ohdm.tasks import async_generate_tile
from ohdm_django_mapnik.ohdm.utily import get_style_xml


class TestAsyncGenerateTile:
    def test_low_zoom(self, test_tile: Dict[str, dict]):
        # clear cache
        cache.clear()

        cache_key: str = "low-zoom"

        async_generate_tile(
            year=test_tile["data"]["year"],
            month=test_tile["data"]["month"],
            day=test_tile["data"]["day"],
            style_xml_template=get_style_xml(
                generate_style_xml=False, carto_style_path=env("CARTO_STYLE_PATH")
            ),
            zoom=0,
            x_pixel=test_tile["data"]["x_pixel"],
            y_pixel=test_tile["data"]["y_pixel"],
            osm_cato_path=env("CARTO_STYLE_PATH"),
            cache_key=cache_key,
        )

        # get tile cache
        tile_cache: Optional[dict] = cache.get(cache_key)

        assert tile_cache is not None
        assert tile_cache["process_id"] is None
        assert tile_cache["tile_hash"] is not None

        assert isinstance(tile_cache["tile_hash"], str)

    def test_high_zoom(self, test_tile: Dict[str, dict]):
        # clear cache
        cache.clear()

        cache_key: str = "high-zoom"

        async_generate_tile(
            year=test_tile["data"]["year"],
            month=test_tile["data"]["month"],
            day=test_tile["data"]["day"],
            style_xml_template=get_style_xml(
                generate_style_xml=False, carto_style_path=env("CARTO_STYLE_PATH")
            ),
            zoom=19,
            x_pixel=test_tile["data"]["x_pixel"],
            y_pixel=test_tile["data"]["y_pixel"],
            osm_cato_path=env("CARTO_STYLE_PATH"),
            cache_key=cache_key,
        )

        # get tile cache
        tile_cache: Optional[dict] = cache.get(cache_key)

        assert tile_cache is not None
        assert tile_cache["process_id"] is None
        assert tile_cache["tile_hash"] is not None

        assert isinstance(tile_cache["tile_hash"], str)
