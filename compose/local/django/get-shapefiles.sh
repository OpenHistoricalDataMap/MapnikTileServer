#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# only for running in docker container
cd /opt/openstreetmap-carto || exit
./scripts/get-shapefiles.py
