#!/bin/bash

sleep 30
osm2pgsql -G --hstore --drop --slim --multi-geometry --style /opt/openstreetmap-carto/openstreetmap-carto.style --tag-transform-script /opt/openstreetmap-carto/openstreetmap-carto.lua --username $PGUSER --database $PGDATABASE --host postgis /opt/pbf/*.pbf

# Create indexes
scripts/indexes.py

# create dev Database
psql -f /update.sql
