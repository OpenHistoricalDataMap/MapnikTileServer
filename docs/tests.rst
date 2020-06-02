Tests
=====

pytest
------

Tests are written with `pytest <https://docs.pytest.org/en/latest/>`_.

The pytests stored in ``ohdm_django_mapnik/ohdm/tests/``.

Before running the test, you need to fill the database with some test data, create
a mapnik style XML and load shape files.::

    $ docker-compose -f local.yml run --rm django /get-shapefiles.sh
    $ docker-compose -f local.yml run --rm django python manage.py create_style_xml
    $ docker-compose -f local.yml run --rm django python manage.py migrate
    $ docker-compose -f local.yml run --rm django python manage.py import_osm --planet /niue-latest.osm.pbf

To run the tests use.::

    $ docker-compose -f local.yml run --rm django pytest

If you want to see the terminal output, you can add ``-s``::

    $ docker-compose -f local.yml run --rm django pytest -s

For testing a folder or single file, add the relative path to the folder or file.::

    $ docker-compose -f local.yml run --rm django pytest ohdm_django_mapnik/ohdm/tests
    $ docker-compose -f local.yml run --rm django pytest ohdm_django_mapnik/ohdm/tests/test_tile.py

For testing a single test in a test file, add the function after ``::``::

    $ docker-compose -f local.yml run --rm django pytest ohdm_django_mapnik/ohdm/tests/test_tile.py::test_tile_generator_init

Mypy
----

From `mypy-lang.org <http://mypy-lang.org/>`_:

    Mypy is an optional static type checker for Python that aims to combine the
    benefits of dynamic (or "duck") typing and static typing. Mypy combines the
    expressive power and convenience of Python with a powerful type system and
    compile-time type checking. Mypy type checks standard Python programs; run
    them using any Python VM with basically no runtime overhead.

On `travis <https://travis-ci.com/>`_ pipeline, the mypy tests will run and
if their some  error, the whole pipeline will show as ``build failed``.

To run mypy::

    $ docker-compose -f local.yml run --rm django mypy ./
