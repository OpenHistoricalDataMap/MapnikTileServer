import_osh
==========

.. warning::
    This command is in experimental state, don't use this in production!

Usage
-----

To import a OpenStreetMap history file (osh), use::

    $ docker-compose -f local.yml run --rm django python manage.py import_osh --clear_rel_db --clear_mapnik_db --rel2pgsql --cache 100000 --planet /osm-files/osh-file.osh.pbf

This command will import a osh file to the relation tables and after that, it will
convert the relation tables to mapnik tables. It is possible to split this into
two command.

To import a osh file into relation tables.::

    $ docker-compose -f local.yml run --rm django python manage.py import_osh --planet /osm-files/osh-file.osh.pbf

.. note::
    Multipolygons are not integrated!

To convert relation tables to mapnik tables.::

    $ docker-compose -f local.yml run --rm django python manage.py import_osh --rel2pgsql

Optional parameters
-------------------

--clear_rel_db
    Clear relation data

--clear_mapnik_db
    Clear mapnik (osm2pgsql) data & tile cache

--cache [CACHE]
    Amount of object witch will be handel at once!

--cache2file
    Cache osmium extraction into a file instead of memory

--planet [PLANET]
    Path to the planet file.

Get osh file
------------

To download a history file for a region like germany, use https://www.geofabrik.de/

To import a complete planet go to https://wiki.openstreetmap.org/wiki/Planet.osm
and choose a mirror, wich support history files.

The osh file should be downloaded into ``../osm-files/``, in the docker enviroment
the folder ``../osm-files/`` will be mounted on ``/osm-files/``.
So to import the file ``../osm-files/germany.osh`` use::

    $ docker-compose -f local.yml run --rm django python manage.py import_osh --planet /osm-files/germany.osh

Because the importer is based on osmium, the file can be compress with ``bz2`` and ``pbf``.
