Setup
=====

Docker
------

Network
^^^^^^^

Every Docker container witch should be accessible from internet need for this project in the `web` network.
To create the network just run::

    $ docker network create web

Build containers
^^^^^^^^^^^^^^^^

To manually build every image (need to be in project directory to work)::

    $ docker-compose build

Tipp: when you build every container, get you a coffee or a cold beer, it will take some time :)

Settings (.env)
---------------

To use settings copy the `.env-example` to `.env`.::

    $ cp .env-example .env

Hostname or Domain of the server::

    # Hostname
    HOSTNAME=localhost

Email address for Let's Encrypt SSL certificate::

    # SSL
    ACME_EMAIL=info@localhost.com

Postgis Database & User::

    # Database
    POSTGRES_USER=ohdm
    POSTGRES_PASSWORD=ohdm

Tile Server& Mapnik style cache time in seconds::

    # cache expire time in seconds ( 604800 seconds == 7 days )
    CAHCE_EXPIRE_TIME=604800

Tile Server debug mode::

    # DEBUG=True
    DEBUG=False

Tile Server tile & mapnik style cache::

    CACHE=True
    # CACHE=False

Start the server
^^^^^^^^^^^^^^^^

After install the requirements & build the docker images you can start the server with (need to be in project directory
to work)::

    $ docker-compose up webserver

In Terminal you can see what is going on on every docker container and if everything work fine, you can the website
on your host domain like ``https://<hostname>/``

To stop the server use ``control`` + ``c``

Start the server in background use::

    $ docker-compose up -d webserver

Adminer Database Interface
^^^^^^^^^^^^^^^^^^^^^^^^^^

To use the ``adminer`` container to edit the database, start at first ``adminer`` in background::

    $ docker-compose up -d adminer-db

Than you can go to ``https://db-admin.<hostname>/`` to enter the ``adminer`` database interface.

For the login data use

+----------+-------------------------------------+
| System   | ``PostgresSQL``                     |
+----------+-------------------------------------+
| Server   | ``postgis``                         |
+----------+-------------------------------------+
| Username | ``POSTGRES_USER`` from ``.env``     |
+----------+-------------------------------------+
| Password | ``POSTGRES_PASSWORD`` from ``.env`` |
+----------+-------------------------------------+
| Database | ``gis``                             |
+----------+-------------------------------------+
