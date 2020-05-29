import hashlib
from typing import Dict, Optional

import pytest

from celery.result import AsyncResult
from config.settings.base import env
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse
from ohdm_django_mapnik.ohdm.tasks import async_generate_tile
from ohdm_django_mapnik.ohdm.tile import TileGenerator
from ohdm_django_mapnik.ohdm.utily import get_style_xml
from ohdm_django_mapnik.ohdm.views import generate_tile


@pytest.mark.django_db()
class TestGenerateTile:
    def get_path(self, kwargs: dict) -> str:
        return reverse("ohdm-tile", kwargs=kwargs,)

    def test_success_empty_cache(
        self, test_tile: Dict[str, dict], tile_generator: TileGenerator
    ):
        # clear cache
        cache.clear()

        request: WSGIRequest = RequestFactory().get(
            self.get_path(kwargs=test_tile["data"])
        )
        response: HttpResponse = generate_tile(
            request=request,
            year=test_tile["data"]["year"],
            month=test_tile["data"]["month"],
            day=test_tile["data"]["day"],
            zoom=test_tile["data"]["zoom"],
            x_pixel=test_tile["data"]["x_pixel"],
            y_pixel=test_tile["data"]["y_pixel"],
        )

        tile_cache: Optional[dict] = cache.get(test_tile["cache"]["cache_key"])
        if tile_cache is None:
            raise AssertionError
        tile: Optional[bytes] = cache.get(tile_cache["tile_hash"])

        tile_generator.zoom = test_tile["data"]["zoom"]
        tile_generator.x_pixel = test_tile["data"]["x_pixel"]
        tile_generator.y_pixel = test_tile["data"]["y_pixel"]

        # check if the right tile was rendert
        if response.content != tile_generator.render_tile():
            raise AssertionError

        # check if the cache was setup right
        if hashlib.md5(response.content).hexdigest() != tile_cache["tile_hash"]:
            raise AssertionError
        if response.content != tile:
            raise AssertionError

        if not isinstance(response.content, bytes):
            raise AssertionError
        if response.status_code != 200:
            raise AssertionError
        if response["content-type"] != "image/jpeg":
            raise AssertionError

    def test_task_already_in_queue(self, test_tile: Dict[str, dict]):
        # clear cache
        cache.clear()

        tile_process: AsyncResult = async_generate_tile.delay(
            year=test_tile["data"]["year"],
            month=test_tile["data"]["month"],
            day=test_tile["data"]["day"],
            style_xml_template=get_style_xml(
                generate_style_xml=False, carto_style_path=env("CARTO_STYLE_PATH")
            ),
            zoom=test_tile["data"]["zoom"],
            x_pixel=test_tile["data"]["x_pixel"],
            y_pixel=test_tile["data"]["y_pixel"],
            osm_cato_path=env("CARTO_STYLE_PATH"),
            cache_key=test_tile["cache"]["cache_key"],
        )

        # set cache with running process
        cache.set(
            test_tile["cache"]["cache_key"],
            {"process_id": tile_process.id, "tile_hash": None},
        )

        request: WSGIRequest = RequestFactory().get(
            self.get_path(kwargs=test_tile["data"])
        )
        response: HttpResponse = generate_tile(
            request=request,
            year=test_tile["data"]["year"],
            month=test_tile["data"]["month"],
            day=test_tile["data"]["day"],
            zoom=test_tile["data"]["zoom"],
            x_pixel=test_tile["data"]["x_pixel"],
            y_pixel=test_tile["data"]["y_pixel"],
        )

        tile_cache: Optional[dict] = cache.get(test_tile["cache"]["cache_key"])

        # check if the cache was setup right
        if tile_cache is None:
            raise AssertionError
        if hashlib.md5(response.content).hexdigest() != tile_process.get():
            raise AssertionError
        if tile_cache["process_id"] is not None:
            raise AssertionError

        if not isinstance(response.content, bytes):
            raise AssertionError
        if response.status_code != 200:
            raise AssertionError
        if response["content-type"] != "image/jpeg":
            raise AssertionError

    def test_tile_in_cache(self, test_tile: Dict[str, dict]):
        # clear cache
        cache.clear()

        # load dummy tile
        dummy_tile: bytes = open(
            "/app/compose/local/django/test_tile/dummy-tile.png", "rb"
        ).read()

        # setup cache
        cache.set(
            test_tile["cache"]["cache_key"],
            {"process_id": None, "tile_hash": test_tile["cache"]["tile_hash"]},
            60,
        )
        cache.set(test_tile["cache"]["tile_hash"], dummy_tile, 60)

        # create tile request
        request: WSGIRequest = RequestFactory().get(
            self.get_path(kwargs=test_tile["data"])
        )
        response: HttpResponse = generate_tile(
            request=request,
            year=test_tile["data"]["year"],
            month=test_tile["data"]["month"],
            day=test_tile["data"]["day"],
            zoom=test_tile["data"]["zoom"],
            x_pixel=test_tile["data"]["x_pixel"],
            y_pixel=test_tile["data"]["y_pixel"],
        )

        # check if the right tile was returned
        if response.content != dummy_tile:
            raise AssertionError

        if not isinstance(response.content, bytes):
            raise AssertionError
        if response.status_code != 200:
            raise AssertionError
        if response["content-type"] != "image/jpeg":
            raise AssertionError

    def test_invalid_url(self, test_tile: Dict[str, dict]):
        # clear cache
        cache.clear()

        request: WSGIRequest = RequestFactory().get(
            self.get_path(kwargs=test_tile["data"])
        )
        response: HttpResponse = generate_tile(
            request=request,
            year=test_tile["data"]["year"],
            month=test_tile["data"]["month"],
            day=test_tile["data"]["day"],
            zoom=test_tile["data"]["zoom"],
            x_pixel=test_tile["data"]["x_pixel"],
            y_pixel=9999,
        )

        if response.status_code != 405:
            raise AssertionError
