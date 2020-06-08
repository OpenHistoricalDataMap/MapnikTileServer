View
====

To change how to handle a tile request, you need to modify the
``ohdm_django_mapnik/ohdm/views.py``.

The default value to render a tile is the function ``generate_tile``. Any
other functions are only for debugging & developing.


If need to change the URL structure, modify the file ``ohdm_django_mapnik/ohdm/urls.py``.

.. note::
    Don't forget to test your changes with ``docker-compose -f local.yml run --rm django pytest -s``
