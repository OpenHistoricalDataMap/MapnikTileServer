URL's
=====

The URL structure of the project is set up in ``config/urls.py`` and
``ohdm_django_mapnik/ohdm/urls.py``.

In the file ``config/urls.py`` there are server wide URL's like ``/admin`` and
in ``ohdm_django_mapnik/ohdm/urls.py`` there are just URL's for the tile server.


Admin panel URL:
    ``/admin``

Time sensitive tile URL:
    ``/tile/<int:year>/<int:month>/<int:day>/<int:zoom>/<float:x_pixel>/<float:y_pixel>/tile.png``

**Only in development mode enabled!**

Tile URL with reload style.xml
    ``/tile/<int:year>/<int:month>/<int:day>/<int:zoom>/<float:x_pixel>/<float:y_pixel>/reload-style-xml/tile.png``

Tile URL with reload project.mml & style.xml
    ``/tile/<int:year>/<int:month>/<int:day>/<int:zoom>/<float:x_pixel>/<float:y_pixel>/reload-project-mml/tile.png``

Tile URL with default openstreetmap-carto (no time sensitivity)
    ``/tile/<int:zoom>/<float:x_pixel>/<float:y_pixel>/tile.png``
