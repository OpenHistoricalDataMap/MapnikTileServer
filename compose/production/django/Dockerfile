# create builder for openstreetmap-carto && noto fonts
FROM node:14-buster-slim as openstreetmap-carto-builder

RUN apt-get update \
  # install python dependencies
  && apt-get install -y --no-install-recommends python3 python3-pip python3-dev \
    python3-setuptools \
  # install mapnik-utils for openstreetmap-carto
  && apt-get install -y --no-install-recommends mapnik-utils \
  # fonts install helper
  && apt-get install -y --no-install-recommends wget unzip \
  # git for downloading openstreetmap-carto
  && apt-get install -y --no-install-recommends git \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# set python 3.x as default
RUN ln -sfn /usr/bin/python3 /usr/bin/python

# set nodejs to stable
RUN npm install -g n stable

# install cartoCSS -> https://github.com/mapbox/carto
RUN npm install -g carto@0

# download openstreetmap-carto & create style.xml
# https://github.com/OpenHistoricalDataMap/openstreetmap-carto
RUN git clone https://github.com/OpenHistoricalDataMap/openstreetmap-carto.git /opt/openstreetmap-carto && \
  cd /opt/openstreetmap-carto && \
  ./scripts/get-shapefiles.py && \
  carto project.mml > style.xml

# https://hub.docker.com/_/debian/
FROM debian:buster-slim

RUN apt-get update \
  # install helper
  && apt-get install -y --no-install-recommends wget unzip fontconfig gnupg \
  # install python dependencies
  && apt-get install -y --no-install-recommends python3-pip python3-dev \
    python3-setuptools \
  # install mapnik-utils for openstreetmap-carto
  && apt-get install -y --no-install-recommends mapnik-utils \
  # dependencies for building Python packages
  && apt-get install -y --no-install-recommends build-essential \
  # psycopg2 dependencies
  && apt-get install -y --no-install-recommends libpq-dev \
  # Translations dependencies
  && apt-get install -y --no-install-recommends gettext \
  # fonts for mapnik
  && apt-get install -y --no-install-recommends fonts-dejavu fonts-hanazono \
    ttf-unifont \
    # noto fonts
    fonts-noto fonts-noto-cjk fonts-noto-cjk-extra fonts-noto-color-emoji \
    fonts-noto-hinted fonts-noto-mono \
    fonts-noto-unhinted \
    fonts-noto-extra fonts-noto-ui-core fonts-noto-ui-extra \
  # geodjango https://docs.djangoproject.com/en/3.0/ref/contrib/gis/install/geolibs/
  && apt-get install -y --no-install-recommends binutils libproj-dev gdal-bin \
  # git for downloading openstreetmap-carto
  && apt-get install -y --no-install-recommends git \
  # mapnik
  && apt-get install -y --no-install-recommends libmapnik-dev libmapnik3.0 mapnik-utils \
    python3-mapnik \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# download osm test area -> https://www.openstreetmap.org/#map=17/53.07300/8.80780
RUN wget 'https://www.openstreetmap.org/api/0.6/map?bbox=8.80616%2C53.07173%2C8.81218%2C53.07477' --output-document '/map.osm'

# install fonts that are not included in the repo
# https://www.google.com/get/noto/
RUN mkdir /opt/noto-fonts \
  && cd /opt/noto-fonts \
  && wget https://noto-website-2.storage.googleapis.com/pkgs/NotoSansBalinese-unhinted.zip \
  && wget https://noto-website-2.storage.googleapis.com/pkgs/NotoSansSyriacEastern-unhinted.zip \
  && wget https://noto-website-2.storage.googleapis.com/pkgs/NotoColorEmoji-unhinted.zip \
  && wget https://noto-website-2.storage.googleapis.com/pkgs/NotoEmoji-unhinted.zip \
  && unzip -o \*.zip \
  && cp ./*.ttf /usr/share/fonts/truetype/noto/ \
  && fc-cache -fv \
  && fc-list \
  && rm -r /opt/noto-fonts

# set python 3.x as default
RUN ln -sfn /usr/bin/python3 /usr/bin/python

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip3 install -r /requirements/system.txt \
  && pip3 install -r /requirements/production.txt

# download openstreetmap-carto
# https://github.com/OpenHistoricalDataMap/openstreetmap-carto
RUN git clone https://github.com/OpenHistoricalDataMap/openstreetmap-carto.git /opt/openstreetmap-carto && \
  cd /opt/openstreetmap-carto && \
  ./scripts/get-shapefiles.py

# create user
RUN groupadd django \
  && useradd -g django django

COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint \
  && chmod +x /entrypoint

COPY --chown=django:django ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start \
  && chmod +x /start

COPY --chown=django:django ./compose/production/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker \
  && chmod +x /start-celeryworker

COPY --chown=django:django ./compose/production/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat \
  && chmod +x /start-celerybeat

COPY --chown=django:django ./compose/production/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower \
  && chmod +x /start-flower

# get openstreetmap-carto from builder
COPY --from=openstreetmap-carto-builder --chown=django:django /opt/openstreetmap-carto/ /opt/openstreetmap-carto/

COPY --chown=django:django . /app

USER django

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
