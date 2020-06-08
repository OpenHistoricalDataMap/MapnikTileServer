clear_cache
===========

.. danger::
    Use this command only when you know what you do! This can't be undone!

With ``docker-compose -f local.yml run --rm django python manage.py clear_cache``
the complete cache will be deleted. Cached files are rendered Tile, previous called
URL's and mapnik style XML for each date.

This is useful when you updated the Mapnik Tables and want to render the new data.
