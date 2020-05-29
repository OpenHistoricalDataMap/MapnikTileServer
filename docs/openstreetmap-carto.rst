Openstreetmap-Carto
===================

The `openstreetmap-carto <https://github.com/gravitystorm/openstreetmap-carto>`_
project is the official repo for the stylesheets of `OpenStreetMap.org <https://www.openstreetmap.org/>`_.

For this project there is a fork of openstreetmap-carto, which can handle the
time request on Postgres SQL. The fork is hostet on github
https://github.com/linuxluigi/openstreetmap-carto/

The only difference between the fork version and the original the file ``/project.mml``.
For each request is an where clause added, which check in the columns ``valid_since``
& ``valid_until`` if the request is for the current date. The data param is added
by ``{{ date.strftime('%Y-%m-%d') }}`` and will be converted in a python script
with jinja2 into the requested date. An example for a modified clause::

    (SELECT
        valid_since,
        valid_until,
        way
        FROM planet_osm_line
        WHERE valid_since <= '{{ date.strftime('%Y-%m-%d') }}'
            AND valid_until >= '{{ date.strftime('%Y-%m-%d') }}'
            AND (man_made = 'cutline')
    ) AS landcover_line
