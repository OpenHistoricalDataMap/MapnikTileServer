prerender
=========

This will be prerendering all Tile to the selected zoom level. To use the
prerendering command use::

    $ docker-compose -f local.yml run --rm django python manage.py prerender [ZOOM_LEVEL]

Change ``[ZOOM_LEVEL]`` to a value between ``0`` to ``19``. A good value will be
between ``5`` to ``13``. The time to prerender all the tiles rise on each level
times 4. This could take a large time to prerender all tiles!
