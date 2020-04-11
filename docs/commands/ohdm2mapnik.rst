ohdm2mapnik
===========

Intro
-----

`ohdm2mapnik` convert a `OHDM database schema
<https://github.com/OpenHistoricalDataMap/OSMImportUpdate/wiki>`_ to a mapnik
readable `Osm2pgsql <https://wiki.openstreetmap.org/wiki/Osm2pgsql/schema>`_
schema.

Database setup
--------------

.. note::
    This project does not contain a option to create a time sensitive OSM database.
    For this purpose use https://github.com/OpenHistoricalDataMap/OSMImportUpdate !

For this command a `OHDM` database connection is need to setup in 
``.envs/.local/.postgres`` for the developing instance and for production is it
``.envs/.production/.postgres``.

An example will look like::

    # OHDM PostgreSQL
    # ------------------------------------------------------------------------------
    OHDM_POSTGRES_HOST=postgres
    OHDM_POSTGRES_PORT=5432
    OHDM_POSTGRES_DB=gis
    OHDM_POSTGRES_USER=docker
    OHDM_POSTGRES_PASSWORD=Dyx8lXMKIGggiQXTzSrAuZ3UsDt8YmLy53WEIAga6EkkVc2GK9lmiRfJxzx7Oahw
    OHDM_POSTGRES_MULTIPLE_EXTENSIONS=postgis,hstore,postgis_topology
    OHDM_PGCONNECT_TIMEOUT=60
    OHDM_SCHEMA=public

Theory
------

For converting the database from OHDM schema to Osm2pgsql (mapnik readbale)
schema, the command will create an SQL statement, which will merge multiple
OHDM tables into one output. 

The tables are ``classification``, ``geoobject``, ``geoobject_geometry`` and 
one of ``points``, ``lines`` or ``polygon``, depending on the ``type_target``
in the ``geoobject_geometry`` table. So if the ``type_target`` is ``0`` or ``1```
it will create points, for 2 lines and 3 it will create polygons.

In :numref:`ohdm2mapnik_OHDM2SingleTable` is an explination, which data are
use for merging the tables.

.. _ohdm2mapnik_OHDM2SingleTable:
.. figure:: _static/ohdm2mapnik_OHDM2SingleTable.png
    :align: center
    :alt: merge ohdm tables into one output
    :figclass: align-center
    :scale: 75%

    merge ohdm tables into one output

As next step, the ``z_order`` will be compute through the given data.
The ``z_order`` is use in mapnik to order the objects for the renderer. So that
a object with a higher ``z_order`` will be overdraw a object with a lower ``z_order``.
To compute the ``z_order``, every classification entry & every tag in ``tags`` will
be go a dict, where is defined how to rank a object. Classification values are
10 times higher rank than the tags. 
In :numref:`ohdm2mapnik_SingleTable2Mapnik` is an diagram how to calc the ``z_order``.

.. _ohdm2mapnik_SingleTable2Mapnik:
.. figure:: _static/ohdm2mapnik_SingleTable2Mapnik.png
    :align: center
    :alt: calc z_order
    :figclass: align-center
    :scale: 75%

    calc z_order

In the same time, when compute the ``z_order``, the system check if the dict which
contains the ``z_order`` values, has a value for ``is_road``. If this is ``true``,
a new ``PlanetOsmRoads`` object will be created from the data in the previous 
generated osm object. 
In :numref:`ohdm2mapnik_planet_osm_roads` is an diagram how a ``PlanetOsmRoads``
object will be created.

.. _ohdm2mapnik_planet_osm_roads:
.. figure:: _static/ohdm2mapnik_planet_osm_roads.png
    :align: center
    :alt: planet_osm_roads
    :figclass: align-center
    :scale: 75%

    planet_osm_roads

The code of the converter is mostly in `ohdm2mapnik.py
<https://github.com/OpenHistoricalDataMap/MapnikTileServer/blob/master/ohdm_django_mapnik/ohdm/ohdm2mapnik.py>`_.

Usage
-----

For production instance use ::

    $ docker-compose -f production.yml run --rm django python manage.py ohdm2mapnik

For local instance use ::

    $ docker-compose -f local.yml run --rm django python manage.py ohdm2mapnik

To clear the mapnik tables befor import, use ``--clear_mapnik_db`::

Optional parameters
...................

To clear the mapnik tables befor import, use ``--clear_mapnik_db`.::

    $ docker-compose -f local.yml run --rm django python manage.py ohdm2mapnik --clear_mapnik_db

To set the cache size ``--cache 100000``, the size how many entries will be saved in RAM bevor adding
them to the database, default value is ``100000``.::

    $ docker-compose -f local.yml run --rm django python manage.py ohdm2mapnik --cache 100000

.. hint::
    To reset just the mapnik tables (``planet_osm_*``) use 
    ``docker-compose -f local.yml run --rm django python manage.py migrate ohdm zero``.
    For faster database testing!