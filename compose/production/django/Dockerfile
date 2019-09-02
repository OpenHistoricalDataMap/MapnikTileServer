# FROM ubuntu:disco
FROM ubuntu:bionic

ENV PYTHONUNBUFFERED 1

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update \
  # psycopg2 dependencies
  && apt-get install -y gcc python3-psycopg2 python-psycopg2 musl-dev \
  && apt-get install -y libpq-dev postgresql-contrib \
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
  && apt-get install -y npm nodejs \

RUN addgroup -S django \
    && adduser -S -G django django

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
RUN npm install -g carto@$0

# install millstone
RUN npm install -g millstone

# https://github.com/gravitystorm/openstreetmap-carto
RUN git clone https://github.com/linuxluigi/openstreetmap-carto.git /opt/openstreetmap-carto  && \
    cd /opt/openstreetmap-carto && \
    ./scripts/get-shapefiles.py

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip3 install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint
RUN chown django /entrypoint

COPY ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
RUN chown django /start
COPY ./compose/production/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker
RUN chown django /start-celeryworker

COPY ./compose/production/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat
RUN chown django /start-celerybeat

COPY ./compose/production/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower
COPY . /app

RUN npm install && npm cache clean --force
RUN npm run build

RUN chown -R django /app
RUN chown -R django /opt/openstreetmap-carto/

RUN python /app/manage.py date_template_importer
RUN carto /opt/openstreetmap-carto/style.mml > /opt/openstreetmap-carto/style.xml

USER django

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
