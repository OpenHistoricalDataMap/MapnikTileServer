View
====

To change how to handle an tile request, you need to modify the
``ohdm_django_mapnik/ohdm/views.py``.

The default value to render a tile is the function ``generate_tile``. Any
other functions are only for debugging & developing.


If need to change the url stucture, modify the file ``ohdm_django_mapnik/ohdm/urls.py``.

.. note::
    Don't forget to test you changes with ``docker-compose -f local.yml run --rm django pytest -s``
