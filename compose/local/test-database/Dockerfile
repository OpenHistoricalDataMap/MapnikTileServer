# https://hub.docker.com/_/ubuntu
# get Ubuntu 18.04
FROM ubuntu:bionic

# setup timezone for tzdata
ARG TIMEZONE
ENV TZ=$TIMEZONE
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Update cache and install dependencies
RUN apt-get update -y && apt-get install -y \
    wget \
    git \
    osm2pgsql \
    python2.7-minimal \
    python-yaml \
    gcc python3-psycopg2 python-psycopg2 musl-dev \
    libpq-dev postgresql-contrib

# Set the osm2pgsql import cache size in MB.
ENV OSM_IMPORT_CACHE 40

# https://github.com/linuxluigi/openstreetmap-carto
RUN mkdir -p /opt/pbf/
RUN git clone https://github.com/linuxluigi/openstreetmap-carto.git /opt/openstreetmap-carto

# copy run script
COPY ./compose/local/test-database/start-up.sh /start-up.sh
RUN chmod +x /start-up.sh

# copy sql scripts
COPY ./compose/local/test-database/sql/ /sql

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

WORKDIR /opt/openstreetmap-carto

# Download Demo Database
RUN wget https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf -O /opt/pbf/berlin-latest.osm.pbf

CMD ["/start-up.sh"]
