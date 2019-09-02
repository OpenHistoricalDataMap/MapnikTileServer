from django.urls import path, register_converter

from ohdm_django_mapnik.ohdm import converters
from . import views
from django.conf import settings

register_converter(converters.FloatConverter, 'float')

urlpatterns = [
    path('<int:year>/<int:month>/<int:day>/<int:zoom>/<float:x_pixel>/<float:y_pixel>/tile.png', views.generate_tile,
         name='generate time sensitive tile'),
]

if settings.DEBUG:
    # url path for developing
    urlpatterns += [
        path('<int:year>/<int:month>/<int:day>/<int:zoom>/<float:x_pixel>/<float:y_pixel>/reload-style-xml/tile.png',
             views.generate_tile_reload_style,
             name='generate time sensitive tile and reload style.xml'),
        path('<int:year>/<int:month>/<int:day>/<int:zoom>/<float:x_pixel>/<float:y_pixel>/reload-project-mml/tile.png',
             views.generate_tile_reload_project,
             name='generate time sensitive tile, generate through project.mml style.xml and reload it'),
        path('<int:zoom>/<float:x_pixel>/<float:y_pixel>/tile.png',
             views.generate_osm_tile,
             name='generate normal osm tile'),
    ]
