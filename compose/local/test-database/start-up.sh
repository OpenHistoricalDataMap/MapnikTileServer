#!/bin/bash

# wait till postgis database is available
if [ -z "${POSTGRES_USER}" ]; then
    base_postgres_image_default_user='postgres'
    export POSTGRES_USER="${base_postgres_image_default_user}"
fi

postgres_ready() {
python3 << END
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
export PGPORT=$POSTGRES_PORT

# delete old configs
rm /ohdm/configs/db_*.txt
cp /ohdm/configs-template/db_*.txt /ohdm/configs/

# set postgres data
sed -i -e "s/PGUSER/$PGUSER/g" /ohdm/configs/db_*.txt
sed -i -e "s/PGPASSWORD/$PGPASSWORD/g" /ohdm/configs/db_*.txt
sed -i -e "s/PGDATABASE/$PGDATABASE/g" /ohdm/configs/db_*.txt
sed -i -e "s/PGHOST/$PGHOST/g" /ohdm/configs/db_*.txt
sed -i -e "s/PGPORT/$PGPORT/g" /ohdm/configs/db_*.txt

# delete old schema
psql -f /ohdm/sql/delete-schema.sql

# create schema
psql -f /ohdm/sql/create-schema.sql

# load osm file into db
java -jar /ohdm/OHDMConverter.jar -o /ohdm/berlin-latest.osm -i /ohdm/configs/db_inter.txt -d /ohdm/configs/db_ohdm.txt

# create rendering tables
java -jar /ohdm/OHDMConverter.jar -d /ohdm/configs/db_ohdm.txt -r /ohdm/configs/db_rendinerng.txt

# fill mapnik tables
java -jar /ohdm/OHDMConverter.jar -r /ohdm/configs/db_rendinerng.txt -m /ohdm/configs/db_mapnik.txt

# delete schema
psql -f /ohdm/sql/delete-schema.sql

exec "$@"
