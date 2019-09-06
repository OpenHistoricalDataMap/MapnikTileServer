from django.core.cache import cache
from config.celery_app import app
from datetime import date
from ohdm_django_mapnik.ohdm.tile import TileGenerator


@app.task
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

    cache.set(
        cache_key,
        TileGenerator(
            request_date=date(year=int(year), month=int(month), day=int(day)),
            style_xml_template=style_xml_template,
            zoom=int(zoom),
            x_pixel=float(x_pixel),
            y_pixel=float(y_pixel),
            osm_cato_path=osm_cato_path,
            cache=True,
        ).render_tile(),
    )

    return cache_key
