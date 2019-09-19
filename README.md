# OHDM Mapnik Tile Server

![https://github.com/OpenHistoricalDataMap/MapnikTileServer/wiki](https://img.shields.io/badge/wiki-read-green.svg)
![https://github.com/OpenHistoricalDataMap/MapnikTileServer/wiki/Setup](https://img.shields.io/badge/Docker--Compose-ready-green.svg) 
![https://github.com/pydanny/cookiecutter-django/](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg)
![https://github.com/ambv/black](https://img.shields.io/badge/code%20style-black-000000.svg)

A time sensitive [Mapnik](https://mapnik.org/) Tile Server written in Python with [Django](https://www.djangoproject.com/).

Based on a Fork of [openstreetmap-carto](https://github.com/linuxluigi/openstreetmap-carto/)

## Features

- work out of the box, no special configuration is needed
- work Linux, MacOS, BSD & also should work Windows (Windows not tested), just need Docker & Docker-Compose to work
- OSM based tile server with time sensitive tiles
- a development & production configuration is included
- tile producer work in extra containers with [celery](http://www.celeryproject.org/) 
- caching tiles by date range in redis
- SSL with Let's Encrypt included
- generate development database from osm 
- include [sentry.io](https://sentry.io/) in production for error tracking

## Dependencies

### Tile Server

- a custom fork of [openstreetmap-carto](https://github.com/linuxluigi/openstreetmap-carto/) for tile styles and SQL
- [https://mapnik.org/](https://mapnik.org/)
- [python-mapnik](https://github.com/mapnik/python-mapnik)
- tile rendering code by [wiki.openstreetmap.org](https://wiki.openstreetmap.org/wiki/Howto_real_time_tiles_rendering_with_mapnik_and_mod_python)
- Project boilerplate by [cookiecutter-django](https://github.com/pydanny/cookiecutter-django/)

### Front-End

- [Bootstrap 4](https://getbootstrap.com/) Theme by [bootswatch.com](https://bootswatch.com/minty/)
- [Leaflet](https://leafletjs.com/) for map view
- [Bootstrap Datepicker](https://github.com/uxsolutions/bootstrap-datepicker)

## Roadmap

- integrate complete test of tile producer, website & [openstreetmap-carto](https://github.com/linuxluigi/openstreetmap-carto/)
- headless server, separate front-end from the back-end maybe with [Ionic](https://ionicframework.com/) and [OpenLayers](https://openlayers.org/)
- add auto test on each commit with [Travis](https://travis-ci.com/) or [Github Actions](https://github.com/features/actions)
- auto update dependencies with [pyup.io](https://pyup.io/)
- update code ``ohdm_django_mapnik/ohdm/tile.py`` to render tile without using deprecated functions like Envelope

## minimum server requirements for developing

- 3 GB of RAM
- 30 GB of free disk space

## install Docker & Docker-Compose

For installing Docker just follow the instructions on [Docker Docs](https://docs.docker.com/install/)

To install Docker-Compose use ``pip``

```bash
$ sudo pip install docker-compose
```

## Setup Development Server

**1. download sourcecode**

```bash
$ mkdir ohdm
$ git clone https://github.com/OpenHistoricalDataMap/MapnikTileServer.git
$ git clone https://github.com/linuxluigi/openstreetmap-carto.git
```

**2. build images**

Building for the first time could take some time, after run the command go and get a coffee.

```bash
$ cd MapnikTileServer
$ docker-compose -f local.yml build
```

**3. create test database (optional)**

```bash
$ docker-compose -f local.yml up test-database
```

**4. start test server**

```bash
$ docker-compose -f local.yml up django celeryworker celerybeat
```

Or start in background.

```bash
$ docker-compose -f local.yml up -d django celeryworker celerybeat
```

If it work fine you should able to visit the Website via http://example.com:8000/

**5. use Flower to monitor tile producing task**

With [Flower](https://flower.readthedocs.io/en/latest/) it's possible to monitor [Celery](http://www.celeryproject.org/) task.

To start the Flower server run:

```bash
$ docker-compose -f local.yml up -d flower
```

Then you can via http://example.com:5555/ visit the Flower monitor. The login data stored in ``.envs/.local/.django``

**6. create admin user**

```bash
$ docker-compose -f local.yml run --rm django python manage.py createsuperuser
```

To visit the admin panel go to http://example.com:8000/admin/

For more infos got to https://cookiecutter-django.readthedocs.io/en/latest/developing-locally-docker.html

## Setup Production Server

**1. download sourcecode** 

```bash
$ mkdir ohdm
$ git clone https://github.com/OpenHistoricalDataMap/MapnikTileServer.git
$ git clone https://github.com/linuxluigi/openstreetmap-carto.git
```

**2. build images**

Building for the first time could take some time, after run the command go and get a coffee.

```bash
$ cd MapnikTileServer
$ docker-compose -f production.yml build
```

**3. setup environment files**

Create 2 environment files

The first is ``.envs/.production/.django``, below is an example how to fill.

```
# General
# ------------------------------------------------------------------------------
# DJANGO_READ_DOT_ENV_FILE=True
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=kt5UXs5t8QEMR6zpa13DNgb0cHJ3u1m3F4yfOO8ggtDq4xp06MjxI1MbUNYPl4Px
DJANGO_ADMIN_URL=geiHZUuftfcy8ZQCsr8qRNG1tXbs9hL2/
DJANGO_ALLOWED_HOSTS=ohdm.net

# Security
# ------------------------------------------------------------------------------
# TIP: better off using DNS, however, redirect is OK too
DJANGO_SECURE_SSL_REDIRECT=False

# Email
# ------------------------------------------------------------------------------
MAILGUN_API_KEY=
DJANGO_SERVER_EMAIL=
MAILGUN_DOMAIN=

# django-allauth
# ------------------------------------------------------------------------------
DJANGO_ACCOUNT_ALLOW_REGISTRATION=True

# django-compressor
# ------------------------------------------------------------------------------
COMPRESS_ENABLED=

# Gunicorn
# ------------------------------------------------------------------------------
WEB_CONCURRENCY=4

# Sentry
# ------------------------------------------------------------------------------
SENTRY_DSN=


# Redis
# ------------------------------------------------------------------------------
REDIS_URL=redis://redis:6379/0

# Celery
# ------------------------------------------------------------------------------

# Flower
CELERY_FLOWER_USER=msshnhBNlGfVLiDTErFKxFWpBOrcZNVp
CELERY_FLOWER_PASSWORD=YG9IuF8qdJaf2Wm2OI1AWdKLv4ddOixmgyKC7y3Kf1PLEfNK3DaQwlpJRe8eh6pL

# ohdm
# ------------------------------------------------------------------------------
CARTO_STYLE_PATH=/opt/openstreetmap-carto
CARTO_STYLE_PATH_DEBUG=/opt/openstreetmap-carto-debug
OSM_CARTO_VERSION=v4.22.0
```

The secound is ``.envs/.production/.postgres``, also below is an example how to fill it.

```
# PostgreSQL
# ------------------------------------------------------------------------------
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=gis
POSTGRES_USER=docker
POSTGRES_PASSWORD=ljloyAbi9HjIuN0AbLC4qaYAPKeFSrMvfUKxbfil1f2OCeZvZBxFZVGVQAkTAXey
POSTGRES_MULTIPLE_EXTENSIONS=postgis,hstore,postgis_topology
```

Please make sure to change at least:

- ``DJANGO_SECRET_KEY``
- ``DJANGO_ADMIN_URL``
- ``CELERY_FLOWER_USER``
- ``CELERY_FLOWER_PASSWORD``
- ``POSTGRES_PASSWORD``

Be careful to change ``POSTGRES_USER`` & ``POSTGRES_USER`` it can may broke the tile server.

**4. start test server**

```bash
$ docker-compose -f local.yml up -d django celeryworker celerybeat
```

The server start on ``https://ohdm.net/``

Also it's possible to start the celery monitor Flower with:

```bash
$ docker-compose -f local.yml up -d flower
```

Flower start on ``https://ohdm.net:5555/``

**5. create admin user**

```bash
$ docker-compose -f production.yml run --rm django python manage.py createsuperuser
```

To visit the admin panel go to http://ohdm.net/geiHZUuftfcy8ZQCsr8qRNG1tXbs9hL2/

The admin panel url depends on the environment var ``DJANGO_ADMIN_URL`` in ``.envs/.production/.django``

**6. Backup**

Go to [cookiecutter-django.readthedocs.io](https://cookiecutter-django.readthedocs.io/en/latest/docker-postgres-backups.html)
to read how to backup the database. 
