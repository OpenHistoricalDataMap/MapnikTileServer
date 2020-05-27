Derployment
==================================

The default way to use the tile-server is with Docker, but it is also possible
to install the system without docker. This tutorial is written for Ubuntu and 
Debian.

**Requirements:**

- Python 3.8
- Postgres 12 with Postgis 3.x
- Redis

1. Install Dependencies
-----------------------

Update your system::

    $ sudo apt-get update
    $ sudo apt-get dist-upgrade

Install helper packages::

    $ sudo apt-get install -y wget unzip fontconfig gnupg

Install node::

    $ sudo apt-get install -y nodejs npm
    $ npm i -g npm@^6

Install python dependencies::

    $ sudo apt-get install -y python3-pip python3-dev python3-setuptools

Install mapnik-utils for openstreetmap-carto::

    $ sudo apt-get install -y mapnik-utils

Install dependencies for building Python packages::

    $ sudo apt-get install -y build-essential

Install psycopg2 dependencies::

    $ sudo apt-get install -y libpq-dev

Install translations dependencies::

    $ sudo apt-get install -y gettext

Geodjango dependencies::

    $ sudo apt-get install -y binutils libproj-dev gdal-bin

Git::

    $ sudo apt-get install -y git

Mapnik::

    $ sudo apt-get install -y libmapnik-dev libmapnik3.0 mapnik-utils python3-mapnik

Fonts for mapnik::

    $ sudo apt-get install -y fonts-dejavu fonts-hanazono ttf-unifont \
        fonts-noto fonts-noto-cjk fonts-noto-cjk-extra fonts-noto-color-emoji \ 
        fonts-noto-hinted fonts-noto-mono fonts-noto-unhinted \
        fonts-noto-extra fonts-noto-ui-core fonts-noto-ui-extra

If you get an error, that a font is missing, you can download it manually
via https://www.google.com/get/noto/. How to enable the fonts, just look at the
next step.

Download extra Noto fonts from google::

    $ mkdir noto-fonts
    $ cd noto-fonts
    $ wget https://noto-website-2.storage.googleapis.com/pkgs/NotoSansBalinese-unhinted.zip
    $ wget https://noto-website-2.storage.googleapis.com/pkgs/NotoSansSyriacEastern-unhinted.zip
    $ wget https://noto-website-2.storage.googleapis.com/pkgs/NotoColorEmoji-unhinted.zip
    $ wget https://noto-website-2.storage.googleapis.com/pkgs/NotoEmoji-unhinted.zip
    $ unzip -o \*.zip \
    $ cp ./*.ttf /usr/share/fonts/truetype/noto/
    $ fc-cache -fv 
    $ fc-list
    $ cd ..
    $ rm -r noto-fonts

2. Install Node dependencies for generating the Mapnik style.xml
----------------------------------------------------------------

Set nodejs to stable::

    $ sudo npm install -g n stable

Install cartoCSS -> https://github.com/mapbox/carto::

    $ sudo npm install -g carto@0

3. Set the default python version
---------------------------------

Set python 3.8 as the default python version. If you don't have python 3.8
try to install it yourself. Python 3.7 should work also, but it is not tested.::

    $ sudo ln -sfn /usr/bin/python3.8 /usr/bin/python

4. Download the Mapnik-Tile-Server & openstreetmap-carto
--------------------------------------------------------

You need to download 3 git packages MapnikTileServer, original openstreetmap-carto
and ohdm version of openstreetmap-carto.

At first download the MapnikTileServer::

    $ git clone https://github.com/OpenHistoricalDataMap/MapnikTileServer.git MapnikTileServer

Next download the original openstreetmap-carto, for testing purpose.::

    $ git clone https://github.com/gravitystorm/openstreetmap-carto.git openstreetmap-carto-debug
    $ cd openstreetmap-carto-debug
    $ git fetch --all
    $ git reset --hard 09623455a392346996a9340e5a4eba8bca9079c6
    $ ./scripts/get-shapefiles.py
    $ carto project.mml > style.xml
    $ cd ..

Now download the ohdm version of openstreetmap-carto::

    $ git clone https://github.com/linuxluigi/openstreetmap-carto.git openstreetmap-carto
    $ cd openstreetmap-carto
    $ ./scripts/get-shapefiles.py
    $ carto project.mml > style.xml
    $ cd ..

5. Install python packages

.. note::
    In this tutorial we install development and production packages, this is not
    recommened, please install a package with fit best for you.

At first go to the MapnikTileServer package & install system packages::

    $ cd MapnikTileServer
    $ pip3 install -r requirements/system.txt

Install development packages::

    $ pip3 install -r requirements/local.txt

Install production packages::

    $ pip3 install -r requirements/production.txt

5. Enable postgres extentions
-----------------------------

Create a Database with the name ``gis`` and run in postgres on the ``gis``
database the following commands::

    $ CREATE EXTENSION postgis;
    $ CREATE EXTENSION hstore;
    $ CREATE EXTENSION postgis_topology;

6. Setup enviroment vars
------------------------

Set the enviroment vars to run a django application::

    $ export CELERY_BROKER_URL="redis://redis:6379/0"
    $ export CARTO_STYLE_PATH="~/openstreetmap-carto"
    $ export CARTO_STYLE_PATH_DEBUG="~/openstreetmap-carto-debug"
    $ export MAPNIK_VERSION=v3.0.22
    $ export TILE_GENERATOR_SOFT_TIMEOUT=240
    $ export TILE_GENERATOR_HARD_TIMEOUT=360

    $ export POSTGRES_HOST=localhost
    $ export POSTGRES_PORT=5432
    $ export POSTGRES_DB=gis
    $ export POSTGRES_USER=!!your-postgres-user!!
    $ export POSTGRES_PASSWORD=!!your-postgres-user-pass!!
    $ export PGCONNECT_TIMEOUT=60

    $ export DATABASE_URL=postgres://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_PORT:$POSTGRES_PORT/$POSTGRES_DB
    $ export OHDM_DATABASE_URL=postgres://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_PORT:$POSTGRES_PORT/$POSTGRES_DB

If you want to run the production version, also add::

    $ export DJANGO_SETTINGS_MODULE=config.settings.production

7. Migrate database
-------------------

Go to the MapnikTileServer folder.::

    $ cd MapnikTileServer

Than run django database migrate::

    $ python manage.py migrate

8. Add a admin user (optional)
------------------------------

Add a user for the admin interface on ``http://localhost:8000/admin/``::

    $ python manage.py createsuperuser

9. Insert a planet or region file (optional)
--------------------------------------------

To fill the database with some test data, just download a ``osm`` file from
http://download.geofabrik.de/

To import the ``osm`` file into the database use::

    $ python manage.py import_osm --planet path-to-your-planet.osm.bz2

This could take some time, depending on how large your file is.

9. Start the Webserver
----------------------

To normal start the server, run::

    $ python manage.py runserver

To use the debug toolbar and more dev features, use instead::

    $ python manage.py runserver_plus
