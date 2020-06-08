from django.conf import settings
from django.urls import path, register_converter
from ohdm_django_mapnik.ohdm import converters

from . import views

register_converter(converters.FloatConverter, "float")

urlpatterns = [
    # a normal tile with using a cache
    path(
        "<int:year>/<int:month>/<int:day>/<int:zoom>/<float:x_pixel>/<float:y_pixel>/tile.png",
        views.generate_tile,
        name="ohdm-tile",
    )
]

if settings.TEST_URLS:
    # url path for developing (no caching)
    urlpatterns += [
        # tile generate with reload style.xml
        path(
            "<int:year>/<int:month>/<int:day>/<int:zoom>/<float:x_pixel>/<float:y_pixel>/reload-style-xml/tile.png",
            views.generate_tile_reload_style,
            name="ohdm-tile-reload-style",
        ),
        # tile generate with reload project.mml & style.xml
        path(
            "<int:year>/<int:month>/<int:day>/<int:zoom>/<float:x_pixel>/<float:y_pixel>/reload-project-mml/tile.png",
            views.generate_tile_reload_project,
            name="ohdm-tile-generate-project.mml-reload-style.xml",
        ),
        # tile generate original openstreetmap-carto
        path(
            "<int:zoom>/<float:x_pixel>/<float:y_pixel>/tile.png",
            views.generate_osm_tile,
            name="osm-normal-tile",
        ),
    ]
