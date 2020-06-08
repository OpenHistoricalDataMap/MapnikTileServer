import_osm
==========

Usage
-----

To import a OpenStreetMap file (osm), use::

    $ docker-compose -f local.yml run --rm django python manage.py import_osm --clear_mapnik_db --planet /osm-files/osm-file.osm.bz2 --cache 100000

This command will import an osm file into mapnik tables.

Optional parameters
...................

--clear_mapnik_db
    Clear mapnik (osm2pgsql) data & tile cache

--cache [CACHE]
    Amount of object which will be handle at once!

--cache2file
    Cache osmium extraction into a file instead of memory

--planet [PLANET]
    Path to the planet file.


Get osm file
------------

To download an osm file for a region like germany, use https://www.geofabrik.de/

To import a complete planet go to https://wiki.openstreetmap.org/wiki/Planet.osm
and choose a mirror.

The osm file should be downloaded into ``../osm-files/``, in the docker enviroment
the folder ``../osm-files/`` will be mounted on ``/osm-files/``.
So to import the file ``../osm-files/germany-latest.osm.bz2`` use::

    $ docker-compose -f local.yml run --rm django python manage.py import_osm --planet /osm-files/germany-latest.osm.bz2

Because the importer is based on osmium, the file can be compressed with ``bz2`` and ``pbf``.
