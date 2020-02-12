# OHDM MapnikTileServer

![https://github.com/OpenHistoricalDataMap/MapnikTileServer/wiki](https://img.shields.io/badge/wiki-read-green.svg)
![https://github.com/OpenHistoricalDataMap/MapnikTileServer/wiki/Setup](https://img.shields.io/badge/Docker--Compose-ready-green.svg)
![https://github.com/pydanny/cookiecutter-django/](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg)
![https://github.com/ambv/black](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Build Status](https://travis-ci.com/linuxluigi/MapnikTileServer.svg?branch=master)](https://travis-ci.com/linuxluigi/MapnikTileServer)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7411526bd5564118acd1fdbf04e6a596)](https://www.codacy.com/manual/linuxluigi/MapnikTileServer?utm_source=github.com&utm_medium=referral&utm_content=linuxluigi/MapnikTileServer&utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/7411526bd5564118acd1fdbf04e6a596)](https://www.codacy.com/manual/linuxluigi/MapnikTileServer?utm_source=github.com&utm_medium=referral&utm_content=linuxluigi/MapnikTileServer&utm_campaign=Badge_Coverage)

The [OpenHistoricalDataMap](https://github.com/OpenHistoricalDataMap)
[MapnikTileServer](https://github.com/OpenHistoricalDataMap/MapnikTileServer) is an
[OpenStreetMap](https://www.openstreetmap.org/) time sensitive fullstack tile server. This means you can go back in time
on a OpenStreetMap Map and see how your city changed since you was a child or you can go much more back in time, it's
your choice :)

The project is build with [Django Cookiecutter](https://github.com/pydanny/cookiecutter-django/) and it comes with
docker support, it is design to work out of the box with Docker.

The current version of this project based on a fork of [openstreetmap-carto](https://github.com/linuxluigi/openstreetmap-carto/).

# Features

- work out of the box, no special configuration is need
- work Linux, MacOS, BSD & also should work Windows (Windows not tested), just need Docker & Docker-Compose to work
- OSM based tile server with time sensitive tiles
- a development & production configuration
- tile producer work in extra containers with [celery](http://www.celeryproject.org/)
- caching tiles by date range in redis
- SSL with Let's Encrypt included
- generate development database from osm
- include [sentry.io](https://sentry.io/) in production for error tracking

# Dependencies

## Tile Server

- a custom fork of [openstreetmap-carto](https://github.com/linuxluigi/openstreetmap-carto/) for tile styles and SQL
- [https://mapnik.org/](https://mapnik.org/)
- [python-mapnik](https://github.com/mapnik/python-mapnik)
- tile rendering code by [wiki.openstreetmap.org](https://wiki.openstreetmap.org/wiki/Howto_real_time_tiles_rendering_with_mapnik_and_mod_python)
- Project boilerplate by [cookiecutter-django](https://github.com/pydanny/cookiecutter-django/)

## Front-End

- [Bootstrap 4](https://getbootstrap.com/) Theme by [bootswatch.com](https://bootswatch.com/minty/)
- [Leaflet](https://leafletjs.com/) for map view
- [Bootstrap Datepicker](https://github.com/uxsolutions/bootstrap-datepicker)

# Roadmap

- integrate complete test of tile producer, website & [openstreetmap-carto](https://github.com/linuxluigi/openstreetmap-carto/)
- a headless server, separate front-end from the back-end maybe with [Ionic](https://ionicframework.com/) and [OpenLayers](https://openlayers.org/)
- add auto test on each commit with [Travis](https://travis-ci.com/) or [Github Actions](https://github.com/features/actions)
- auto update dependencies with [pyup.io](https://pyup.io/)
- update code `ohdm_django_mapnik/ohdm/tile.py` to render tile without using deprecated functions like Envelope
- scale redis cache

# minimum server requirements for developing

- 3 GB of RAM
- 30 GB of free disk space

# Project Structure

```
OHDM MapnikTileServer
│   .coveragerc                                  # https://coverage.readthedocs.io/en/v4.5.x/config.html
│   .dockerignore                                # https://docs.docker.com/engine/reference/builder/#dockerignore-file
│   .editorconfig                                # https://editorconfig.org/
│   .gitignore                                   # https://git-scm.com/docs/gitignore
│   .pylintrc                                    # https://www.pylint.org/
│   .travis.yml                                  # travis bionic image https://docs.travis-ci.com/user/reference/bionic/
│   LICENSE
│   local.yml                                    # docker-compose file for developing https://cookiecutter-django.readthedocs.io/en/latest/developing-locally-docker.html
│   manage.py                                    # Django start file
│   merge_production_dotenvs_in_dotenv.py        # https://cookiecutter-django.readthedocs.io/en/latest/developing-locally-docker.html?highlight=merge_production_dotenvs_in_dotenv#configuring-the-environment
│   production.yml                               # docker-compose file for production https://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html
│   pytest.ini                                   # https://pytest.org/en/latest/
│   README.md
│   requirements.txt                             # python production requirements (mostly needed for heroku)
│   setup.cfg                                    # https://docs.pytest.org/en/latest/customize.html
│   LICENSE
│
└───.envs
│   └───.local
│   │   │   .django                              # default enviroment vars for django
│   │   │   .postgres                            # default enviroment vars for postgres
│   └───.production                              # need to create, not there by default
│   │   │   .django                              # custom enviroment vars for django
│   │   │   .postgres                            # custom enviroment vars for django
│
└───compose                                      # docker build files
│
└───config                                       # django settings
│
└───locale                                       # https://docs.djangoproject.com/en/2.2/topics/i18n/translation/
│
└───ohdm_django_mapnik                           # main project folder
│   └───contrib                                  # http://cookiecutter-django.readthedocs.io/en/latest/faq.html#why-is-there-a-django-contrib-sites-directory-in-cookiecutter-django
│   └───ohdm                                     # ohdm app for django
│   │   admin.py                                 # model admin interface designer https://docs.djangoproject.com/en/2.2/ref/contrib/admin/
│   │   apps.py                                  # app config https://docs.djangoproject.com/en/2.2/ref/applications/#configuring-applications
│   │   converters.py                            # regex converter
│   │   models.py                                # django models
│   │   tasks.py                                 # celery task https://docs.celeryproject.org/en/latest/userguide/tasks.html
│   │   tests.py                                 # test file
│   │   tile.py                                  # tile producer logic
│   │   urls.py                                  # app url logic
│   │   views.py                                 # app view logic
│   │   └───management                           # app commands folder
│   │   │   │   date_template_importer.py        # convert openstreetmap-carto/project.mml to a ohdm version (not working right now)
│   │   └───migrations                           # Django model migrations (no not edit manually) https://docs.djangoproject.com/en/2.2/topics/migrations/
│   └───static                                   # static files like JS & CSS for website to publish https://docs.djangoproject.com/en/2.2/howto/static-files/
│   └───templates                                # HTML website templates https://docs.djangoproject.com/en/2.2/topics/templates/
│   └───users                                    # custom user model by https://github.com/pydanny/cookiecutter-django
│
└───requirements                                 # python requirements https://pip.pypa.io/en/stable/user_guide/#requirements-files
│   │   base.txt                                 # requirements for dev & productions
│   │   local.txt                                # requirements for dev
│   │   production.txt                           # requirements for productions
```

## URL Structure

URL's are setup in `config/urls.py` and `ohdm_django_mapnik/ohdm/urls.py`.

```
/                                                                                                                # Landingpage
/about/                                                                                                          # Aboutpage
/users/                                                                                                          # user urls
/accounts/                                                                                                       # allauth url
/tile/<int:year>/<int:month>/<int:day>/<int:zoom>/<float:x_pixel>/<float:y_pixel>/tile.png                       # tile url

# only in development mode enabled
/tile/<int:year>/<int:month>/<int:day>/<int:zoom>/<float:x_pixel>/<float:y_pixel>/reload-style-xml/tile.png      # tile url with reload style.xml
/tile/<int:year>/<int:month>/<int:day>/<int:zoom>/<float:x_pixel>/<float:y_pixel>/reload-project-mml/tile.png    # tile url with reload project.mml & style.xml
/tile/<int:zoom>/<float:x_pixel>/<float:y_pixel>/tile.png                                                        # tile url with default openstreetmap-carto (no time sensitivity)
```

Tile example link (in Berlin): http://example.com/tile/2010/02/16/13/4398/2685/tile.png

# Setup

## Install Docker & Docker-Compose

For installing Docker just follow the instructions on [Docker Docs](https://docs.docker.com/install/)

To install Docker-Compose use `pip`

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

**3. init database**

```bash
$ docker-compose -f local.yml run --rm django python manage.py migrate
```

**4. create test database (optional)**

```bash
$ docker-compose -f local.yml up test-database
```

**5. download shapefiles & generate style.xml**

```bash
$ docker-compose -f local.yml run --rm django /get-shapefiles.sh
$ docker-compose -f local.yml run --rm django python manage.py create_style_xml
```

**6. start test server**

```bash
$ docker-compose -f local.yml up django celeryworker celerybeat
```

Or start in background.

```bash
$ docker-compose -f local.yml up -d django celeryworker celerybeat
```

If it works fine you should able to visit the Website via http://example.com:8000/

**5. use Flower to monitor tile producing task**

With [Flower](https://flower.readthedocs.io/en/latest/) it's possible to monitor [Celery](http://www.celeryproject.org/) task.

To start the Flower server run:

```bash
$ docker-compose -f local.yml up -d flower
```

Then you can via http://example.com:5555/ watch the Flower monitor. The login data stored in `.envs/.local/.django`

**6. create admin user**

```bash
$ docker-compose -f local.yml run --rm django python manage.py createsuperuser
```

To visit the admin panel go to http://example.com:8000/admin/

For more infos got to https://cookiecutter-django.readthedocs.io/en/latest/developing-locally-docker.html

**7. stop server**

```bash
$ docker-compose -f local.yml stop
```

## Setup Production Server

Please read also the doc on [cookiecutter-django](https://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html)
for more details.

**1. download sourcecode**

```bash
$ mkdir ohdm
$ git clone https://github.com/OpenHistoricalDataMap/MapnikTileServer.git
```

**2. build images**

Building for the first time could take some time, after run the command go and get coffee.

```bash
$ cd MapnikTileServer
$ docker-compose -f production.yml build
```

**3. setup environment files**

Create 2 environment files

The first is `.envs/.production/.django`, below is an example how to fill.

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
TILE_GENERATOR_SOFT_TIMEOUT=240
TILE_GENERATOR_HARD_TIMEOUT=360
```

The second is `.envs/.production/.postgres`, also below is an example how to fill it.

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

- `DJANGO_SECRET_KEY`
- `DJANGO_ADMIN_URL`
- `CELERY_FLOWER_USER`
- `CELERY_FLOWER_PASSWORD`
- `POSTGRES_PASSWORD`

Be careful to change `POSTGRES_USER` & `POSTGRES_USER` it can may broke the tile server.

**4. start production server**

```bash
$ docker-compose -f production.yml up -d django celeryworker celerybeat traefik
```

The server start on `https://ohdm.net/`

Also it's possible to start the celery monitor Flower with:

```bash
$ docker-compose -f production.yml up -d flower
```

Flower start on `https://ohdm.net:5555/`

**5. create Database**

```bash
$ docker-compose -f production.yml run --rm django python manage.py migrate
```

**6. create admin user**

```bash
$ docker-compose -f production.yml run --rm django python manage.py createsuperuser
```

To visit the admin panel go to http://ohdm.net/geiHZUuftfcy8ZQCsr8qRNG1tXbs9hL2/

The admin panel url depends on the environment var `DJANGO_ADMIN_URL` in `.envs/.production/.django`

**7. Backup**

Go to [cookiecutter-django.readthedocs.io](https://cookiecutter-django.readthedocs.io/en/latest/docker-postgres-backups.html)
to read how to back up the database.

**8. stop server**

```bash
$ docker-compose -f production.yml stop
```

## Scale-Up for production

A tile server need a lot of resources and a big database. So for a better performance use a beefy server or use docker
swarm / kubernetes for scaling.

To scale up use the comments below for the django and celeryworker containers.

```bash
$ docker-compose -f production.yml scale django=4
$ docker-compose -f production.yml scale celeryworker=2
```

Don’t try to scale `postgres`, `celerybeat`, or `traefik`!

# Testing

To read how to run test go to [cookiecutter-django](https://cookiecutter-django.readthedocs.io/en/latest/testing.html)

Or for running test manual use `docker-compose -f local.yml run django pytest`

Also the project include a working travis test.

# Docs

To create the docs use:

```bash
$ docker-compose -f local.yml run django make --directory docs html
```
