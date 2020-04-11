import_osm
==========

Usage
-----

To import a OpenStreetMap file (osm), use::

    $ docker-compose -f local.yml run --rm django python manage.py import_osm --clear_mapnik_db --planet /osm-files/osm-file.osm.bz2 --cache 100000

This command will import a osm file into mapnik tables.

Optional parameters
-------------------

``--clear_mapnik_db`` will delete mapnik tables befor convert relation tables.

``--cache 100000`` set the cache size, how many objects will be hold in ram befor
insert them into database. The default value is ``100000``.

Get osm file
------------

To download a osm file for a region like germany, use https://www.geofabrik.de/

To import a complete planet go to https://wiki.openstreetmap.org/wiki/Planet.osm
and choose a mirror.

The osm file should be downloaded into ``../osm-files/``, in the docker enviroment
the folder ``../osm-files/`` will be mounted on ``/osm-files/``.
So to import the file ``../osm-files/germany-latest.osm.bz2`` use::

    $ docker-compose -f local.yml run --rm django python manage.py import_osm --planet /osm-files/germany-latest.osm.bz2

Because the importer is based on osmium, the file can be compress with ``bz2`` and ``pbf``.