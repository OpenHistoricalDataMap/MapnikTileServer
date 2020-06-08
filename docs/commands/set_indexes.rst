set_indexes
===========

To speedup the tile rendering, set indexes on the osm tables.::

    $ docker-compose -f local.yml run --rm django python manage.py set_indexes
