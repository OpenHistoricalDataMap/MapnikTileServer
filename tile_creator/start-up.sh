#!/bin/bash

# import all pbf files to db
# --flat-nodes -> for planet import
osm2pgsql -G --hstore --drop --slim --multi-geometry --style /openstreetmap-carto/openstreetmap-carto.style --tag-transform-script /openstreetmap-carto/openstreetmap-carto.lua --username $PGUSER --database $POSTGRES_DB --host postgis --password /pbf/*.pbf << EOF
$PGPASSWORD
EOF

carto project.mml > /mapnik-xml/mapnik.xml

# endless loop for debug
if [ $ALWAYS_ON == 'True' ]
then
   echo "always on mode -> True"
   while :
   do
       sleep 1
   done
else
   echo "always on mode -> False"
fi
