Deployment with Docker
======================

.. note::
    The article is based on https://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html

Prerequisites
-------------

* Docker 17.05+.
* Docker Compose 1.17+

Download the software
---------------------

To download the source, use git with.::

    $ git clone https://github.com/OpenHistoricalDataMap/MapnikTileServer.git

Configuration with environment vars
-----------------------------------

To set up the server for your personal needs, you need to create 2 files.
``.envs/.production/.django`` & ``.envs/.production/.postgres``.

All possible environment vars are list in :ref:`settings`. A minimal config file
``.envs/.production/.django`` will look like::

    # General
    # ------------------------------------------------------------------------------
    USE_DOCKER=yes
    IPYTHONDIR=/app/.ipython
    DJANGO_SECRET_KEY=!!!ChangeMeToSomeRandomValue!!!!!
    DJANGO_ALLOWED_HOSTS=a.ohdm.net,b.ohdm.net,c.ohdm.net
    DJANGO_SETTINGS_MODULE=config.settings.production

    # Redis
    # ------------------------------------------------------------------------------
    REDIS_URL=redis://redis:6379/0

    # ohdm
    # ------------------------------------------------------------------------------
    CARTO_STYLE_PATH=/opt/openstreetmap-carto

In the ``.envs/.production/.postgres`` file is the connection to the PostGis server
and the schema of the OHDM data included. For the minimal configuration.::

    # Default PostgreSQL
    # ------------------------------------------------------------------------------
    POSTGRES_HOST=postgres
    POSTGRES_PORT=5432
    POSTGRES_DB=gis
    POSTGRES_USER=docker
    POSTGRES_PASSWORD=Dyx8lXMKIGggiQXTzSrAuZ3UsDt8YmLy53WEIAga6EkkVc2GK9lmiRfJxzx7Oahw
    POSTGRES_MULTIPLE_EXTENSIONS=postgis,hstore,postgis_topology
    PGCONNECT_TIMEOUT=60

    # OHDM PostgreSQL
    # ------------------------------------------------------------------------------
    OHDM_SCHEMA=ohdm

More possible options can be read on `docker-postgis <https://github.com/kartoza/docker-postgis>`_.

Need to change
..............

DJANGO_SECRET_KEY
    Need to be randomly unique value to provide cryptographic signing.
    For creating a randomly-generated SECRET_KEY, you can use https://djecrety.ir/

    Docs: https://docs.djangoproject.com/en/3.0/ref/settings/#std:setting-SECRET_KEY

DJANGO_ALLOWED_HOSTS
    Domains for the django container, add all domains which are pointed to the container,
    separated by ``,``.

Monitoring
..........

There a two monitoring system integrated.
`Flower <https://flower.readthedocs.io/en/latest/>`_ monitor the tile producing queue
and `Sentry.io <https://sentry.io>`_ for logging all errors on sentry.io.
For setup go to :ref:`monitoring`.

Changing the default domains
----------------------------

To change the default domains, you need to modify ``compose/production/traefik/traefik.yml```
and set the enviroment var ``DJANGO_ALLOWED_HOSTS``.

Building & Running Production Stack
-----------------------------------

You will need to build the stack first. To do that, run::

    $ docker-compose -f production.yml build

Once this is ready, you can run it with::

    $ docker-compose -f production.yml up

To run the stack and detach the containers, run::

    $ docker-compose -f production.yml up -d

To run a migration, open up a second terminal and run::

   $ docker-compose -f production.yml run --rm django python manage.py migrate

To create a superuser, run::

   $ docker-compose -f production.yml run --rm django python manage.py createsuperuser

If you need a shell, run::

   $ docker-compose -f production.yml run --rm django python manage.py shell

To check the logs out, run::

   $ docker-compose -f production.yml logs

If you want to scale your application, run::

   $ docker-compose -f production.yml scale django=70
   $ docker-compose -f production.yml scale celeryworker=2

.. warning:: don't try to scale ``postgres``, ``celerybeat``, or ``traefik``.

To see how your containers are doing run::

    $ docker-compose -f production.yml ps

Example: Supervisor
-------------------

Once you are ready with your initial setup, you want to make sure that your application is run by a process manager to
survive reboots and auto restarts in case of an error. You can use the process manager you are most familiar with. All
it needs to do is to run ``docker-compose -f production.yml up`` in your projects root directory.

If you are using ``supervisor``, you can use this file as a starting point::

    [program:MapnikTileServer]
    command=docker-compose -f production.yml up
    directory=/path/to/MapnikTileServer
    redirect_stderr=true
    autostart=true
    autorestart=true
    priority=10

Move it to ``/etc/supervisor/conf.d/MapnikTileServer.conf`` and run::

    $ supervisorctl reread
    $ supervisorctl update
    $ supervisorctl start MapnikTileServer

For status check, run::

    $ supervisorctl status
