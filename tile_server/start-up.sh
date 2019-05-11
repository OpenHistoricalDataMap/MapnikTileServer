#!/bin/bash

# wait till database is online
python3 /isDatabaseOn.py

# import all /opt/pbf/*.pbf to database
if [ $IMPORT == 'true' ]
then
   # todo add an option to drop old data

   echo "Import all pbf files to Database"
   # import all pbf files to db
   # --flat-nodes -> for planet import
   osm2pgsql -G --hstore --drop --slim --multi-geometry --style /opt/openstreetmap-carto/openstreetmap-carto.style --tag-transform-script /opt/openstreetmap-carto/openstreetmap-carto.lua --username $PGUSER --database $PGDATABASE --host postgis /opt/pbf/*.pbf
fi

# pre render all tiles
if [ $RENDER == 'true' ]
then
   echo "Import all pbf files to Database"
   renderd -f -c /usr/local/etc/renderd.conf
   render_list -n 1 -z 0 -Z 10 -a
fi

# start webserver with mod_tile
if [ $RUN_WEBSERVER == 'true' ]
then
   service apache2 start
   renderd -f -c /usr/local/etc/renderd.conf
fi
