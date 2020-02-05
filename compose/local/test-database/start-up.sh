#!/bin/bash

# wait till postgis database is available
if [ -z "${POSTGRES_USER}" ]; then
    base_postgres_image_default_user='postgres'
    export POSTGRES_USER="${base_postgres_image_default_user}"
fi

postgres_ready() {
python << END
import sys

import psycopg2

try:
    psycopg2.connect(
        dbname="${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
        host="${POSTGRES_HOST}",
        port="${POSTGRES_PORT}",
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)

END
}
until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  sleep 1
done
>&2 echo 'PostgreSQL is available'

export PGUSER=$POSTGRES_USER
export PGPASSWORD=$POSTGRES_PASSWORD
export PGDATABASE=$POSTGRES_DB
export PGHOST=$POSTGRES_HOST

# create dev Database
psql -f /sql/drop-osm.sql

osm2pgsql -G --hstore --drop --slim --multi-geometry --style /opt/openstreetmap-carto/openstreetmap-carto.style --tag-transform-script /opt/openstreetmap-carto/openstreetmap-carto.lua --username $PGUSER --database $PGDATABASE --host $POSTGRES_HOST /opt/pbf/*.pbf

# Create indexes
scripts/indexes.py

# create dev Database
psql -f /sql/update.sql

exec "$@"
