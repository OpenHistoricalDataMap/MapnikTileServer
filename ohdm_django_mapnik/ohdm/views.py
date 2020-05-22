from datetime import date
from time import sleep
from typing import Optional

from celery import exceptions
from celery.result import AsyncResult
from config.settings.base import OSM_CARTO_STYLE_XML, env
from django.core.cache import cache
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from ohdm_django_mapnik.ohdm.exceptions import CoordinateOutOfRange
from ohdm_django_mapnik.ohdm.tasks import async_generate_tile
from ohdm_django_mapnik.ohdm.tile import TileGenerator
from ohdm_django_mapnik.ohdm.utily import get_style_xml


@cache_page(env.int("CACHE_VIEW"))
def generate_tile(
    request, year: int, month: int, day: int, zoom: int, x_pixel: float, y_pixel: float
) -> HttpResponse:
    """
    get a mapnik tile, get it from cache if exist else it will be generated as a celery task
    :param request: django request
    :param year: request year as INT
    :param month: request month as INT
    :param day: request day as INT
    :param zoom: mapnik zoom level
    :param x_pixel: mapnik x coordinate
    :param y_pixel: mapnik y coordinate
    :return:
    """

    # set tile cache key, where the celery task id & tile cache id is stored
    tile_cache_key: str = "{}-{}-{}-{}-{}-{}".format(
        int(year), int(month), int(day), int(zoom), int(x_pixel), int(y_pixel),
    )

    # tile static typing
    tile: Optional[bytes]
    tile_process: AsyncResult

    # get tile cache
    tile_cache: Optional[dict] = cache.get(
        tile_cache_key, {"process_id": None, "tile_hash": None}
    )

    # check if process is running and wait for end
    if tile_cache:
        if tile_cache["process_id"]:
            tile_process = AsyncResult(tile_cache["process_id"])
            for _ in range(0, env.int("TILE_GENERATOR_HARD_TIMEOUT") * 2):
                sleep(0.5)
                tile_cache = cache.get(
                    tile_cache_key, {"process_id": None, "tile_hash": None}
                )

                if tile_cache:
                    if tile_cache["tile_hash"]:
                        break

    # try get tile png & return it
    if tile_cache:
        if tile_cache["tile_hash"]:
            tile = cache.get(tile_cache["tile_hash"])
            if tile:
                return HttpResponse(tile, content_type="image/jpeg")

    # if there is no tile process & no tile in cache, create one
    tile_process = async_generate_tile.delay(
        year=int(year),
        month=int(month),
        day=int(day),
        style_xml_template=OSM_CARTO_STYLE_XML,
        zoom=int(zoom),
        x_pixel=float(x_pixel),
        y_pixel=float(y_pixel),
        osm_cato_path=env("CARTO_STYLE_PATH"),
        cache_key=tile_cache_key,
    )

    if not tile_cache:
        tile_cache = {"process_id": None, "tile_hash": None}

    tile_cache["process_id"] = tile_process.id

    # update cache
    if zoom <= env.int("ZOOM_LEVEL"):
        cache.set(tile_cache_key, tile_cache, None)
    else:
        cache.set(tile_cache_key, tile_cache, env.int("TILE_CACHE_TIME"))

    try:
        tile_process.wait(timeout=env.int("TILE_GENERATOR_HARD_TIMEOUT"))
    except exceptions.TimeoutError:
        return HttpResponse("Timeout when creating tile", status=500)
    except CoordinateOutOfRange as e:
        return HttpResponse(e, status=405)

    tile_cache["tile_hash"] = tile_process.get()
    tile = cache.get(tile_cache["tile_hash"])
    if tile:
        return HttpResponse(tile, content_type="image/jpeg")

    return HttpResponse("Caching Error", status=500)


def generate_tile_reload_style(
    request, year: int, month: int, day: int, zoom: int, x_pixel: float, y_pixel: float
) -> HttpResponse:
    """
    reload style.xml & than generate a new mapnik tile
    :param request: django request
    :param year: request year as INT
    :param month: request month as INT
    :param day: request day as INT
    :param zoom: mapnik zoom level
    :param x_pixel: mapnik x coordinate
    :param y_pixel: mapnik y coordinate
    :return:
    """
    # generate time sensitive tile and reload style.xml
    tile_gen: TileGenerator = TileGenerator(
        request_date=date(year=int(year), month=int(month), day=int(day)),
        style_xml_template=get_style_xml(
            generate_style_xml=False, carto_style_path=env("CARTO_STYLE_PATH")
        ),
        zoom=int(zoom),
        x_pixel=float(x_pixel),
        y_pixel=float(y_pixel),
        osm_cato_path=env("CARTO_STYLE_PATH"),
    )

    return HttpResponse(tile_gen.render_tile(), content_type="image/jpeg")


def generate_tile_reload_project(
    request, year: int, month: int, day: int, zoom: int, x_pixel: float, y_pixel: float
) -> HttpResponse:
    """
    generate reload style.xml & than generate a new mapnik tile
    :param request: django request
    :param year: request year as INT
    :param month: request month as INT
    :param day: request day as INT
    :param zoom: mapnik zoom level
    :param x_pixel: mapnik x coordinate
    :param y_pixel: mapnik y coordinate
    :return:
    """

    tile_gen: TileGenerator = TileGenerator(
        request_date=date(year=int(year), month=int(month), day=int(day)),
        style_xml_template=get_style_xml(
            generate_style_xml=True, carto_style_path=env("CARTO_STYLE_PATH")
        ),
        zoom=int(zoom),
        x_pixel=float(x_pixel),
        y_pixel=float(y_pixel),
        osm_cato_path=env("CARTO_STYLE_PATH"),
    )

    return HttpResponse(tile_gen.render_tile(), content_type="image/jpeg")


def generate_osm_tile(
    request, zoom: int, x_pixel: float, y_pixel: float
) -> HttpResponse:
    """
    get a default mapnik tile, without check the valid date
    :param request:
    :param zoom:
    :param x_pixel:
    :param y_pixel:
    :return:
    """
    # generate normal osm tile
    tile_gen: TileGenerator = TileGenerator(
        request_date=date(year=2000, month=1, day=1),
        style_xml_template=get_style_xml(
            generate_style_xml=False, carto_style_path=env("CARTO_STYLE_PATH_DEBUG")
        ),
        zoom=int(zoom),
        x_pixel=float(x_pixel),
        y_pixel=float(y_pixel),
        osm_cato_path=env("CARTO_STYLE_PATH_DEBUG"),
    )

    return HttpResponse(tile_gen.render_tile(), content_type="image/jpeg")
