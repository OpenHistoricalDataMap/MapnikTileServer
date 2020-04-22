Tests
=====

Tests are written with `pytest <https://docs.pytest.org/en/latest/>`_.

The tests are stored in ``ohdm_django_mapnik/ohdm/tests/``.

To run the tests use::

    $ docker-compose -f local.yml run --rm django pytest

If you want to see the terminal output, you cann add ``-s``::

    $ docker-compose -f local.yml run --rm django pytest -s

To tests a folder or single file, add the relativ path to the folder or file::

    $ docker-compose -f local.yml run --rm django pytest ohdm_django_mapnik/ohdm/tests
    $ docker-compose -f local.yml run --rm django pytest ohdm_django_mapnik/ohdm/tests/test_tile.py

To tests a single test in a test file, add the funktion after ``::``::

    $ docker-compose -f local.yml run --rm django pytest ohdm_django_mapnik/ohdm/tests/test_tile.py::test_tile_generator_init
