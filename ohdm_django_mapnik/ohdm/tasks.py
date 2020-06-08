import hashlib
from datetime import date

from config.celery_app import app
from config.settings.base import env
from django.core.cache import cache
from ohdm_django_mapnik.ohdm.tile import TileGenerator


@app.task(
    soft_time_limit=env.int("TILE_GENERATOR_SOFT_TIMEOUT", 240),
    time_limit=env.int("TILE_GENERATOR_HARD_TIMEOUT", 360),
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

    # render requested tile
    tile: bytes = TileGenerator(
        request_date=date(year=int(year), month=int(month), day=int(day)),
        style_xml_template=style_xml_template,
        zoom=int(zoom),
        x_pixel=float(x_pixel),
        y_pixel=float(y_pixel),
        osm_cato_path=osm_cato_path,
        use_cache=True,
    ).render_tile()

    # create a md5 hash of the tile
    tile_hash: str = hashlib.md5(tile).hexdigest()

    # set url-tile cache content
    tile_cache: dict = {"process_id": None, "tile_hash": tile_hash}

    # update tile cache & url-tile cache content
    if zoom <= env.int("ZOOM_LEVEL", 13):
        # cache for ever
        cache.set(tile_hash, tile, None)
        cache.set(cache_key, tile_cache, None)
    else:
        # cache for time in TILE_CACHE_TIME
        cache.set(tile_hash, tile, env.int("TILE_CACHE_TIME", 2592000) * 10)
        cache.set(cache_key, tile_cache, env.int("TILE_CACHE_TIME", 2592000))

    return tile_hash
