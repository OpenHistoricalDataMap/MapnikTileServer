from datetime import date, timedelta

from config.settings.base import OSM_CARTO_STYLE_XML, env
from ohdm_django_mapnik.ohdm.models import (
    PlanetOsmLine,
    PlanetOsmPoint,
    PlanetOsmPolygon,
)
from ohdm_django_mapnik.ohdm.tasks import async_generate_tile


def prerender(zoom_level: int):
    # get the lowest valid_since for each geometry
    point_valid_since: PlanetOsmPoint = PlanetOsmPoint.objects.all().order_by(
        "valid_since"
    )[0]
    line_valid_since: PlanetOsmLine = PlanetOsmLine.objects.all().order_by(
        "valid_since"
    )[0]
    polygon_valid_since: PlanetOsmPolygon = PlanetOsmPolygon.objects.all().order_by(
        "valid_since"
    )[0]

    # get the highest valid_until for each geometry
    point_valid_until: PlanetOsmPoint = PlanetOsmPoint.objects.all().order_by(
        "-valid_until"
    )[0]
    line_valid_until: PlanetOsmLine = PlanetOsmLine.objects.all().order_by(
        "-valid_until"
    )[0]
    polygon_valid_until: PlanetOsmPolygon = PlanetOsmPolygon.objects.all().order_by(
        "-valid_until"
    )[0]

    # get the lowest valid_since for all geometries
    valid_since: date = point_valid_since.valid_since
    if line_valid_since.valid_since < valid_since:
        valid_since = line_valid_since.valid_since
    if polygon_valid_since.valid_since < valid_since:
        valid_since = polygon_valid_since.valid_since

    # get the highest valid_until for all geometries
    valid_until: date = point_valid_until.valid_until
    if line_valid_until.valid_until < valid_until:
        valid_until = line_valid_until.valid_until
    if polygon_valid_until.valid_until < valid_since:
        valid_until = polygon_valid_until.valid_until

    print("Start prerender")
    delta = timedelta(days=1)
    while valid_since <= valid_until:
        for zoom in range(0, zoom_level + 1):
            for x in range(0, zoom * zoom + 1):
                for y in range(0, zoom * zoom + 1):
                    tile_cache_key: str = "{}-{}-{}-{}-{}-{}".format(
                        valid_since.year,
                        valid_since.month,
                        valid_since.day,
                        zoom,
                        x,
                        y,
                    )

                    async_generate_tile.delay(
                        year=valid_since.year,
                        month=valid_since.month,
                        day=valid_since.day,
                        style_xml_template=OSM_CARTO_STYLE_XML,
                        zoom=zoom,
                        x_pixel=x,
                        y_pixel=y,
                        osm_cato_path=env("CARTO_STYLE_PATH"),
                        cache_key=tile_cache_key,
                    )

        valid_since += delta
    print("prerending queue is set!")
