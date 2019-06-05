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

To manually build every container::

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
