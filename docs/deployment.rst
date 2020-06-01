Deployment
==================================

.. note::
    This tutorial is only tested on Debian Buster!

Firewall
--------

Ports ``80`` & ``443`` need to be open, for installing the dependencies & running
the server. An example for iptables to open the ports.::

    $ iptables -A INPUT -p tcp --dport 443 -j ACCEPT
    $ iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT
    $ iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    $ iptables -A OUTPUT -p tcp --dport 80 -j ACCEPT

Dependend Services
------------------

Postgres 12 with Postgis 3
..........................

To use the performence boost of the new Postgres Version, add the
`postgres repo <https://www.postgresql.org/download/linux/debian/>`_
from postgresql.org to your system.::


    $ apt-get --no-install-recommends install \
        locales gnupg2 wget ca-certificates rpl pwgen software-properties-common gdal-bin iputils-ping
    $ sh -c "echo \"deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main\" > /etc/apt/sources.list.d/pgdg.list"
    $ wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    $ apt-get update

Install Postgres 12 with Postgis 3::

    $ apt-get --no-install-recommends install postgresql-client-12 \
        postgresql-common postgresql-12 postgresql-12-postgis-3 \
        netcat postgresql-12-ogr-fdw postgresql-12-postgis-3-scripts \
        postgresql-12-cron postgresql-plpython3-12 postgresql-12-pgrouting

Postgres service is started & set to come up after each system reboot::

    $ systemctl status postgresql.service

While the installation, the user ``postgres`` was added to the system. With the
user you can access the admin postgres user.

    $ su - postgres

Change the postgres user ``postgres`` password (remember this password!)::

    $ psql -c "alter user postgres with password 'YourNewPassword'"

Now access the postgres prompt::

    $ psql

Enable Postgis & hstore extentions for postgres::

    $ CREATE EXTENSION postgis;
    $ CREATE EXTENSION hstore;
    $ CREATE EXTENSION postgis_topology;

Create the ``gis`` database with the user ``mapnik`` to access the ``gis`` database.::

    $ CREATE DATABASE gis;
    $ CREATE USER mapnik WITH ENCRYPTED PASSWORD 'MyStr0ngP@SS';
    $ GRANT ALL PRIVILEGES ON DATABASE gis to mapnik;

Set the new ``mapnik`` database user as superuser::

    $ ALTER USER mapnik WITH SUPERUSER;

Logout from postgres prompt & user::

    $ \q
    $ exit

Redis 5
.......

Redis use as a caching server for the tiles & as a task broker for celery.

For installing redis server, use::

    $ apt-get install --no-install-recommends redis-server

If you running redis on the same system than the web-service, than is redis ready
to work :)


NGINX
......

Install NGINX and certbot for Let's Encrypt::

    $ apt-get install --no-install-recommends nginx python3-acme \
        python3-certbot python3-mock python3-openssl python3-pkg-resources \
        python3-pyparsing python3-zope.interface python3-certbot-nginx

Obtaining an SSL Certificate::

    $ certbot --nginx -d a.ohdm.net -d b.ohdm.net -d c.ohdm.net

Create a NGINX config file for ohdm.::

    $ nano /etc/nginx/sites-available/MapnikTileServer.conf

    server {
        server_name a.ohdm.net b.ohdm.net c.ohdm.net;

        location = /favicon.ico { access_log off; log_not_found off; }
        location  /static/ {
        alias /home/mapnik/MapnikTileServer/staticfiles/;
        }

        location / {
            include proxy_params;
        proxy_pass http://unix:/home/mapnik/MapnikTileServer/MapnikTileServer.sock;
        }

        listen 443 ssl; # managed by Certbot
        ssl_certificate /etc/letsencrypt/live/a.ohdm.net/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/a.ohdm.net/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    }
    server {
        if ($host = c.ohdm.net) {
            return 301 https://$host$request_uri;
        } # managed by Certbot

        if ($host = b.ohdm.net) {
            return 301 https://$host$request_uri;
        } # managed by Certbot

        if ($host = a.ohdm.net) {
            return 301 https://$host$request_uri;
        } # managed by Certbot

        listen 80;
        server_name a.ohdm.net b.ohdm.net c.ohdm.net;
        return 404; # managed by Certbot
    }

Link the config file from ``/etc/nginx/sites-available/MapnikTileServer.conf``
to ``/etc/nginx/sites-enabled/MapnikTileServer.conf``::

    $ ln -s /etc/nginx/sites-available/MapnikTileServer.conf /etc/nginx/sites-enabled

Test if the config was setup right & restart NGINX::

    $ nginx -t
    $ systemctl restart nginx

Test if certbot can auto reniew the SSL certificate::

    $ certbot renew --dry-run

Install MapnikTileServer
------------------------

System dependencies::

    $ apt-get install --no-install-recommends wget unzip fontconfig gnupg

Node::

    $ apt-get install nodejs npm
    $ npm i -g npm@^6

Python::

    $ apt-get install --no-install-recommends python3-pip python3-dev \
        python3-setuptools

Mapnik-utils for openstreetmap-carto::

    $ apt-get install --no-install-recommends mapnik-utils

Dependencies for building Python packages::

    $ apt-get install --no-install-recommends build-essential

Psycopg2 dependencies::

    $ apt-get install --no-install-recommends libpq-dev

Translations dependencies::

    $ apt-get install --no-install-recommends gettext

Fonts for mapnik::

    $ apt-get install --no-install-recommends fonts-dejavu fonts-hanazono \
    ttf-unifont \
    fonts-noto fonts-noto-cjk fonts-noto-cjk-extra fonts-noto-color-emoji \
    fonts-noto-hinted fonts-noto-mono \
    fonts-noto-unhinted \
    fonts-noto-extra fonts-noto-ui-core fonts-noto-ui-extra

`Geodjango <https://docs.djangoproject.com/en/3.0/ref/contrib/gis/install/geolibs/>`_::

    $ apt-get install --no-install-recommends binutils libproj-dev gdal-bin

Git::

    $ apt-get install --no-install-recommends git

Mapnik::

    $ apt-get install --no-install-recommends libmapnik-dev libmapnik3.0 mapnik-utils \
    python3-mapnik

Supervisor::

    $ apt-get install --no-install-recommends supervisor

Download & install more `noto fonts <https://www.google.com/get/noto/>`_ for mapnik::

    $ mkdir noto-fonts
    $ cd noto-fonts
    $ wget https://noto-website-2.storage.googleapis.com/pkgs/NotoSansBalinese-unhinted.zip
    $ wget https://noto-website-2.storage.googleapis.com/pkgs/NotoSansSyriacEastern-unhinted.zip
    $ wget https://noto-website-2.storage.googleapis.com/pkgs/NotoColorEmoji-unhinted.zip
    $ wget https://noto-website-2.storage.googleapis.com/pkgs/NotoEmoji-unhinted.zip
    $ unzip -o \*.zip
    $ cp ./*.ttf /usr/share/fonts/truetype/noto/
    $ fc-cache -fv
    $ fc-list
    $ cd ..
    $ rm -r noto-fonts

Update NodeJS to the latest stable::

    $ npm install -g n stable

Install `CartoCSS <https://github.com/mapbox/carto>`_ with a version below 1::

    $ npm install -g carto@0

Set enviroment vars for running the MapnikTileServer::

    $ nano /etc/environment

Fill the ``/etc/environment`` file with the following values.

    # Django
    # ------------------------------------------------------------------------------
    DJANGO_READ_DOT_ENV_FILE=True
    DJANGO_SETTINGS_MODULE=config.settings.production

Create a Mapnik user, for running the MapnikTileServer::

    $ adduser mapnik

Log into ``mapnik`` user and go to the home folder::

    $ su - mapnik
    $ cd

Download `openstreetmap-carto <https://github.com/linuxluigi/openstreetmap-carto/>`_::

    $ git clone https://github.com/linuxluigi/openstreetmap-carto.git

Go to the new openstreetmap-carto folder, download the shapefiles & create
the default mapnik style XML::

    $ cd openstreetmap-carto
    $ ./scripts/get-shapefiles.py
    $ carto project.mml > style.xml

Next go back to the ``mapnik`` home foldder::

    $ cd

Download `MapnikTileServer <https://github.com/OpenHistoricalDataMap/MapnikTileServer/>`_
and go to the new MapnikTileServer folder::

    $ git clone https://github.com/OpenHistoricalDataMap/MapnikTileServer.git
    $ cd MapnikTileServer

Install / update the python packages as root user::

    $ exit
    $ pip3 install -r /home/mapnik/MapnikTileServer/requirements/system.txt
    $ pip3 install -r /home/mapnik/MapnikTileServer/requirements/production.txt

.. note::
    When install an update of MapnikTileServer, also update the python packages!

Go back to the ``mapnik`` user & back to the MapnikTileServer folder::

    $ su mapnik
    $ cd /home/mapnik/MapnikTileServer

Create a ``.env`` file for the MapnikTileServer settings. Go to :ref:`settings`
to see all possibiles options. Below is a minimal configuration::

    # General
    # ------------------------------------------------------------------------------
    DJANGO_SECRET_KEY=!!!ChangeMeToSomeRandomValue!!!!!
    DJANGO_ALLOWED_HOSTS=a.ohdm.net,b.ohdm.net,c.ohdm.net

    # Redis
    # ------------------------------------------------------------------------------
    REDIS_URL=redis://localhost:6379/0

    # ohdm
    # ------------------------------------------------------------------------------
    CARTO_STYLE_PATH=/home/mapnik/openstreetmap-carto

    # Default PostgreSQL
    # ------------------------------------------------------------------------------
    DATABASE_URL="postgres://mapnik:MyStr0ngP@SS@localhost:5432/gis"
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    POSTGRES_DB=gis
    POSTGRES_USER=mapnik
    POSTGRES_PASSWORD=MyStr0ngP
    PGCONNECT_TIMEOUT=60

    # OHDM PostgreSQL
    # ------------------------------------------------------------------------------
    OHDM_SCHEMA=ohdm

Tests the settings, migrate the database, set indexes & collect static files::

    $ python3 manage.py migrate
    $ python3 manage.py set_indexes
    $ python3 manage.py collectstatic

Add a superuser for the admin panel::

    $ python3 manage.py createsuperuser

Add ``supervisor`` script to auto start django, celery & flower at system start.
For creating the scripts, go back to the root user::

    $ exit

Open the text editor to create the ``supervisor`` file.::

    $ nano /etc/supervisor/conf.d/mapnik_tile_server.conf

Fill the ``supervisor`` file with the values below, but don't forget to change ``CELERY_FLOWER_USER```
& ``CELERY_FLOWER_PASSWORD`` values::

    [supervisord]
    environment=DJANGO_READ_DOT_ENV_FILE=True,DJANGO_SETTINGS_MODULE=config.settings.production,CELERY_FLOWER_USER=ChangeMeFlowerUser,CELERY_FLOWER_PASSWORD=ChangeMeFlowerPassword,CELERY_BROKER_URL=redis://localhost:6379/0

    [program:MapnikTileServer_celery_worker]
    command=celery -A config.celery_app worker -l INFO
    user=mapnik
    directory=/home/mapnik/MapnikTileServer
    autostart=true
    autorestart=true
    priority=10
    stderr_logfile=/var/log/MapnikTileServer_celery_worker.err.log

    [program:MapnikTileServer_celery_beat]
    command=celery -A config.celery_app beat -l INFO
    user=mapnik
    directory=/home/mapnik/MapnikTileServer
    autostart=true
    autorestart=true
    priority=10
    stderr_logfile=/var/log/MapnikTileServer_celery_beat.err.log

    [program:MapnikTileServer_celery_flower]
    command=celery flower --app=config.celery_app --broker="redis://localhost:6379/0" --basic_auth="${CELERY_FLOWER_USER}:${CELERY_FLOWER_PASSWORD}"
    user=mapnik
    directory=/home/mapnik/MapnikTileServer
    autostart=true
    autorestart=true
    priority=10
    stderr_logfile=/var/log/MapnikTileServer_celery_flower.err.log

    [program:MapnikTileServer_django]
    command=/usr/local/bin/gunicorn config.wsgi --workers 2 --bind unix:/home/mapnik/MapnikTileServer/MapnikTileServer.sock -t 240
    user=mapnik
    directory=/home/mapnik/MapnikTileServer
    autostart=true
    autorestart=true
    priority=10
    stderr_logfile=/var/log/MapnikTileServer_django.err.log

To enable the ``supervisor`` script.::

    supervisorctl reread
    supervisorctl update
    supervisorctl start MapnikTileServer_celery_worker
    supervisorctl start MapnikTileServer_celery_beat
    supervisorctl start MapnikTileServer_celery_flower
    supervisorctl start MapnikTileServer_django
    supervisorctl status

Use commands
------------

For using django commands from :ref:`commands`, log into the ``mapnik`` user &
go to the ``/home/mapnik/MapnikTileServer``.::

    $ su mapnik
    $ cd /home/mapnik/MapnikTileServer

The commands in :ref:`commands` are written for the docker usage, to use them
without docker, just use the command after the ``django`` keyword. For exmaple,
to use ``set_indexes``, in the docs the command is write down as
``docker-compose -f local.yml run --rm django python manage.py set_indexes`` and
to use it without docker, just use ``python3 manage.py set_indexes``.

Download updates
----------------

Stop all services first::

    $ supervisorctl stop all

Log into the ``mapnik`` user and go to the openstreetmap-carto folder::

    $ su mapnik
    $ cd /home/mapnik/openstreetmap-carto

Get the latest version with ``git pull``::

    $ git fetch
    $ git pull

Downoad the latest shapefiles & create the default mapnik style XML::

    $ ./scripts/get-shapefiles.py
    $ carto project.mml > style.xml

Go to the MapnikTileServer::

    $ cd /home/mapnik/MapnikTileServer

Download the latest code from github, for the MapnikTileServer::

    $ git fetch
    $ git pull

Update the database & staticfiles::

    $ python3 manage.py migrate
    $ python3 manage.py set_indexes
    $ python3 manage.py collectstatic

Log out from the ``mapnik`` user & start the webservices again::

    $ exit
    $ supervisorctl start all
