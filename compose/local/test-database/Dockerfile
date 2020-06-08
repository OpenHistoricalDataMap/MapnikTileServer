# https://hub.docker.com/_/openjdk
FROM openjdk:15-jdk-alpine3.11

# find new packges use latest branch (not edge!) -> https://pkgs.alpinelinux.org/packages
# install git & bash
RUN apk add --no-cache \
    # wget -> download demo dataset & OHDMConverter
    wget \
    # bash -> run a shell
    bash \
    # python -> check if posgres is reachable
    python3 musl-dev gcc python3-dev musl-dev \
    postgresql-dev postgresql-client

RUN pip3 install psycopg2

RUN mkdir /ohdm

WORKDIR /ohdm

# download demo dataset (niue)
RUN wget http://download.geofabrik.de/australia-oceania/niue-latest.osm.bz2  \
    && bunzip2 niue-latest.osm.bz2

# download OHDMConverter
RUN wget https://github.com/OpenHistoricalDataMap/OSMImportUpdate/releases/download/0.1/OHDMConverter.jar

# copy run script
COPY ./compose/local/test-database/start-up.sh /start-up.sh
RUN chmod +x /start-up.sh

# copy sql scripts
COPY ./compose/local/test-database/sql/ /ohdm/sql

# copy configs
COPY ./compose/local/test-database/configs/ /ohdm/configs-template
RUN mkdir /ohdm/configs

WORKDIR /opt/openstreetmap-carto

CMD ["/start-up.sh"]
