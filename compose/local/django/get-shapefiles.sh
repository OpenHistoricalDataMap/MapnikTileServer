#!/bin/bash

# only for running in docker container
cd /opt/openstreetmap-carto || exit
./scripts/get-shapefiles.py
