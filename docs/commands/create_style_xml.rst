Create Mapnik Style XML
=======================

To debug the ``project.mml`` from ``openstreetmap-carto``, use::

    $ docker-compose -f local.yml run --rm django python manage.py create_sytle_xml

This command will create a new mapnik ``sytle.xml`` with ``carto``. Only useful when
debugging ``project.mml``.