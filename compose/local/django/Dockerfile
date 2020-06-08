# https://hub.docker.com/_/debian/
FROM debian:buster-slim

RUN apt-get update \
  # install helper
  && apt-get install -y --no-install-recommends wget unzip fontconfig gnupg \
  # install node
  && apt-get install -y nodejs npm \
  && npm i -g npm@^6 \
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

# download demo dataset (niue)
RUN wget http://download.geofabrik.de/australia-oceania/niue-latest.osm.pbf -O /niue-latest.osm.pbf

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

# set nodejs to stable
RUN npm install -g n stable

# install cartoCSS -> https://github.com/mapbox/carto
RUN npm install -g carto@0

# download orginal openstreetmap-carto & create default style.xml
# https://github.com/gravitystorm/openstreetmap-carto
RUN git clone https://github.com/gravitystorm/openstreetmap-carto.git /opt/openstreetmap-carto-debug  && \
  cd /opt/openstreetmap-carto-debug && \
  git fetch --all && \
  git checkout 09623455a392346996a9340e5a4eba8bca9079c6 && \
  ./scripts/get-shapefiles.py && \
  carto project.mml > style.xml

# folder for https://github.com/OpenHistoricalDataMap/openstreetmap-carto
RUN mkdir /opt/openstreetmap-carto

COPY ./compose/local/django/get-shapefiles.sh /get-shapefiles.sh
RUN sed -i 's/\r$//g' /get-shapefiles.sh \
  && chmod +x /get-shapefiles.sh

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip3 install -r /requirements/system.txt \
  && pip3 install -r /requirements/local.txt

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint \
  && chmod +x /entrypoint

COPY ./compose/local/django/start /start
RUN sed -i 's/\r$//g' /start \
  && chmod +x /start

COPY ./compose/local/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker \
  && chmod +x /start-celeryworker

COPY ./compose/local/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat \
  && chmod +x /start-celerybeat

COPY ./compose/local/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower \
  && chmod +x /start-flower

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
