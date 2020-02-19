from datetime import date
from typing import Optional

from celery.result import AsyncResult
from django.core.cache import cache
from django.http import HttpResponse

from config.settings.base import OSM_CARTO_STYLE_XML, env
from ohdm_django_mapnik.ohdm.models import TileCache
from ohdm_django_mapnik.ohdm.tasks import async_generate_tile
from ohdm_django_mapnik.ohdm.tile import TileGenerator
from ohdm_django_mapnik.ohdm.utily import get_style_xml


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

    request_date: date = date(year=int(year), month=int(month), day=int(day))

    tile_cache: Optional[TileCache] = TileCache.objects.filter(
        zoom=zoom,
        x_pixel=x_pixel,
        y_pixel=y_pixel,
        valid_since__lte=request_date,
        valid_until__gte=request_date,
    ).last()

    if tile_cache:
        tile: Optional[bytes] = tile_cache.get_tile_from_cache_or_delete()

    if tile_cache and tile:
        return HttpResponse(tile, content_type="image/jpeg")
    else:
        tile_cache = TileCache.objects.create(
            zoom=zoom,
            x_pixel=x_pixel,
            y_pixel=y_pixel,
            valid_since=request_date,
            valid_until=request_date,
        )

        tile_process: AsyncResult = async_generate_tile.delay(
            year=int(year),
            month=int(month),
            day=int(day),
            style_xml_template=OSM_CARTO_STYLE_XML,
            zoom=int(zoom),
            x_pixel=float(x_pixel),
            y_pixel=float(y_pixel),
            osm_cato_path=env("CARTO_STYLE_PATH"),
            cache_key=tile_cache.get_cache_key(),
        )

        tile_cache.celery_task_id = tile_process.id
        tile_cache.save()
        tile_cache.set_valid_date()

        while tile_process.ready() is False:
            pass

        tile_cache.celery_task_done = True
        tile_cache.save()

        return HttpResponse(cache.get(tile_process.get()), content_type="image/jpeg")


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
            generate_style_xml=False, carto_sytle_path=env("CARTO_STYLE_PATH")
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
            generate_style_xml=True, carto_sytle_path=env("CARTO_STYLE_PATH")
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
            generate_style_xml=False, carto_sytle_path=env("CARTO_STYLE_PATH_DEBUG")
        ),
        zoom=int(zoom),
        x_pixel=float(x_pixel),
        y_pixel=float(y_pixel),
        osm_cato_path=env("CARTO_STYLE_PATH_DEBUG"),
    )

    return HttpResponse(tile_gen.render_tile(), content_type="image/jpeg")
