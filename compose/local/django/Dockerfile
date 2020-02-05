# FROM ubuntu:disco
FROM ubuntu:bionic

ENV PYTHONUNBUFFERED 1

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update \
  # psycopg2 dependencies
  && apt-get install -y gcc python3-psycopg2 python-psycopg2 musl-dev \
  && apt-get install -y libpq-dev \
  # python3
  && apt-get install -y python3 python3-pip python3-dev \
  # Pillow dependencies
  && apt-get install -y libjpeg8-dev zlib1g-dev libtiff-dev libfreetype6 libfreetype6-dev libwebp-dev libopenjp2-7-dev libopenjp2-7-dev \
  # CFFI dependencies
  && apt-get install -y libffi-dev python-cffi cl-cffi \
  # Translations dependencies
  && apt-get install -y gettext \
  # https://docs.djangoproject.com/en/dev/ref/django-admin/#dbshell
  && apt-get install -y postgresql-client \
  # https://docs.djangoproject.com/en/2.2/ref/contrib/gis/install/geolibs/
  && apt-get install -y binutils libproj-dev gdal-bin \
  # fonts
  && apt-get install -y fonts-dejavu-core fonts-hanazono fonts-noto-cjk fonts-noto-cjk-extra fonts-noto-color-emoji \
  && apt-get install -y fonts-noto-hinted fonts-noto-unhinted fontconfig psf-unifont ttf-unifont typecatcher unifont xfonts-unifont \
  # git
  && apt-get install -y git \
  # mapnik
  && apt-get install -y libmapnik3.0 libmapnik-dev mapnik-utils python3-mapnik \
  # nodejs
  && apt-get install -y npm nodejs

# install Noto Sans fonts
RUN git clone https://github.com/googlei18n/noto-emoji.git /opt/noto-emoji && \
    cp /opt/noto-emoji/fonts/NotoEmoji-Regular.ttf /usr/share/fonts/truetype/noto/NotoEmoji-Regular.ttf && \
    fc-cache -fv && \
    fc-list && \
    rm -r /opt/noto-emoji

# set python 3.x as default
RUN ln -sfn /usr/bin/python3 /usr/bin/python

# set nodejs to stable
RUN npm install -g n stable

# install cartoCSS -> https://github.com/mapbox/carto
RUN npm install -g carto@0

# install millstone
RUN npm install -g millstone

# dir for https://github.com/linuxluigi/openstreetmap-carto
RUN mkdir /opt/openstreetmap-carto

# https://github.com/gravitystorm/openstreetmap-carto
ARG OSM_CARTO_VERSION
RUN git clone https://github.com/gravitystorm/openstreetmap-carto.git /opt/openstreetmap-carto-debug  && \
    cd /opt/openstreetmap-carto-debug && \
    git fetch --all && \
    git checkout $OSM_CARTO_VERSION && \
    ./scripts/get-shapefiles.py && \
    carto project.mml > style.xml

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip3 install -r /requirements/local.txt

COPY ./compose/local/django/get-shapefiles.sh /get-shapefiles.sh
RUN chmod +x /get-shapefiles.sh

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./compose/local/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./compose/local/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./compose/local/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

WORKDIR /app

ENTRYPOINT ["/entrypoint"]

