from datetime import date
from time import sleep

from django.core.cache import cache

from config.celery_app import app
from config.settings.base import env
from ohdm_django_mapnik.ohdm.tile import TileGenerator


@app.task(
    soft_time_limit=env.int("TILE_GENERATOR_SOFT_TIMEOUT"),
    time_limit=env.int("TILE_GENERATOR_HARD_TIMEOUT"),
)
def async_generate_tile(
    year: int,
    month: int,
    day: int,
    style_xml_template: str,
    zoom: int,
    x_pixel: float,
    y_pixel: float,
    osm_cato_path: str,
    cache_key: str,
) -> str:
    """
    run celery background task to generate a mapnik tile & cache the tile
    :param year: request year as INT
    :param month: request month as INT
    :param day: request day as INT
    :param style_xml_template: path to style.xml
    :param zoom: mapnik zoom level
    :param x_pixel: mapnik x coordinate
    :param y_pixel: mapnik y coordinate
    :param osm_cato_path: path to osm cato
    :param cache_key: cache key for mapnik tile
    :return:
    """

    cache.set(
        cache_key,
        TileGenerator(
            request_date=date(year=int(year), month=int(month), day=int(day)),
            style_xml_template=style_xml_template,
            zoom=int(zoom),
            x_pixel=float(x_pixel),
            y_pixel=float(y_pixel),
            osm_cato_path=osm_cato_path,
            use_cache=True,
        ).render_tile(),
    )

    return cache_key


@app.task()
def auto_done_task(seconds: int = 0):
    """
    Test task witch auto finish in x seconds
    
    Keyword Arguments:
        seconds {int} -- time to sleep (default: {0})
    """
    sleep(seconds)
