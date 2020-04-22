URL's
=====

The URL structure of the project is setup in ``config/urls.py`` and 
``ohdm_django_mapnik/ohdm/urls.py``. 

In the file ``config/urls.py`` there are server wide urls like ``/admin`` and
in ``ohdm_django_mapnik/ohdm/urls.py`` there are just urls for the tile server.


Admin panel URL:
    ``/admin``

Time sensitiv tile URL:
    ``/tile/<int:year>/<int:month>/<int:day>/<int:zoom>/<float:x_pixel>/<float:y_pixel>/tile.png``

**Only in development mode enabled!**

Tile url with reload style.xml
    ``/tile/<int:year>/<int:month>/<int:day>/<int:zoom>/<float:x_pixel>/<float:y_pixel>/reload-style-xml/tile.png``

Tile url with reload project.mml & style.xml
    ``/tile/<int:year>/<int:month>/<int:day>/<int:zoom>/<float:x_pixel>/<float:y_pixel>/reload-project-mml/tile.png``

Tile url with default openstreetmap-carto (no time sensitivity) 
    ``/tile/<int:zoom>/<float:x_pixel>/<float:y_pixel>/tile.png``
