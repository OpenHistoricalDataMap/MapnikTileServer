Frontend
=====================================

.. index:: Angular
.. index:: Frontend

The demo frontend is written as an Angular app. The source code is in a extra
git repo https://github.com/linuxluigi/ohdm-angular-frontend

For handling the tile request to the MapntikTileServer it use the libary
`OpenLayers <https://openlayers.org/>`_. The sourcecode for the map handling
is in `map.component.ts <https://github.com/linuxluigi/ohdm-angular-frontend/blob/master/src/app/map/map.component.ts>`_.

.. figure:: _static/frontend.png
    :alt: angular frontend
    :align: center

    angular frontend

For faster tile request, use mutiple domains. Each Webbrowser has a limit how
many ``HTTP`` connection can be use at once. To extend the limits, use mutiple
domains. In OpenLayers you can set a mutiple domains in an array with ``OlXYZ``.::

    this.source = new OlXYZ({
        urls: [
            "https://a.ohdm.net/" + mapDate.year + "/" + mapDate.month + "/" + mapDate.day + "/{z}/{x}/{y}/tile.png",
            "https://b.ohdm.net/" + mapDate.year + "/" + mapDate.month + "/" + mapDate.day + "/{z}/{x}/{y}/tile.png",
            "https://c.ohdm.net/" + mapDate.year + "/" + mapDate.month + "/" + mapDate.day + "/{z}/{x}/{y}/tile.png",
        ],
    });
