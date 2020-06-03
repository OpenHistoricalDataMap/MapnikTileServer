from typing import Dict

import pytest
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse
from ohdm_django_mapnik.ohdm.views import (
    generate_osm_tile,
    generate_tile_reload_project,
    generate_tile_reload_style,
)


@pytest.mark.django_db()
def test_generate_tile_reload_style(test_tile: Dict[str, dict]):
    # clear cache
    cache.clear()

    path: str = reverse("ohdm-tile-reload-style", kwargs=test_tile["data"])

    request: WSGIRequest = RequestFactory().get(path)
    response: HttpResponse = generate_tile_reload_style(
        request=request,
        year=test_tile["data"]["year"],
        month=test_tile["data"]["month"],
        day=test_tile["data"]["day"],
        zoom=test_tile["data"]["zoom"],
        x_pixel=test_tile["data"]["x_pixel"],
        y_pixel=test_tile["data"]["y_pixel"],
    )

    if not isinstance(response.content, bytes):
        raise AssertionError
    if response.status_code != 200:
        raise AssertionError
    if response["content-type"] != "image/jpeg":
        raise AssertionError


@pytest.mark.django_db()
def test_generate_tile_reload_project(test_tile: Dict[str, dict]):
    # clear cache
    cache.clear()

    path: str = reverse(
        "ohdm-tile-generate-project.mml-reload-style.xml", kwargs=test_tile["data"]
    )

    request: WSGIRequest = RequestFactory().get(path)
    response: HttpResponse = generate_tile_reload_project(
        request=request,
        year=test_tile["data"]["year"],
        month=test_tile["data"]["month"],
        day=test_tile["data"]["day"],
        zoom=test_tile["data"]["zoom"],
        x_pixel=test_tile["data"]["x_pixel"],
        y_pixel=test_tile["data"]["y_pixel"],
    )

    if not isinstance(response.content, bytes):
        raise AssertionError
    if response.status_code != 200:
        raise AssertionError
    if response["content-type"] != "image/jpeg":
        raise AssertionError


@pytest.mark.django_db()
def test_generate_osm_tile(test_tile: Dict[str, dict]):
    # clear cache
    cache.clear()

    path: str = reverse("osm-normal-tile", kwargs=test_tile["no-data-data"])

    request: WSGIRequest = RequestFactory().get(path)
    response: HttpResponse = generate_osm_tile(
        request=request,
        zoom=test_tile["no-data-data"]["zoom"],
        x_pixel=test_tile["no-data-data"]["x_pixel"],
        y_pixel=test_tile["no-data-data"]["y_pixel"],
    )

    if not isinstance(response.content, bytes):
        raise AssertionError
    if response.status_code != 200:
        raise AssertionError
    if response["content-type"] != "image/jpeg":
        raise AssertionError
