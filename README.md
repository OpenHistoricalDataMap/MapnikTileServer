# OHDM-Docker

It's a `docker-compose` repo for the new version of http://www.ohdm.net/, but it's just the beginning, so
do what you want and get back later :)

## Quickstart

**1. create** `.env`

Copy `.env-example` to `.env` and change it to you needs

```bash
$ cp .env-example .env
$ vim .env
```

**2. Download a** `*.pbf` **file to** `./pbf`

```bash
$ wget https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf -O pbf/berlin-latest.osm.pbf
```

**3. Build Docker Image**

```bash
$ docker-compose build
```

**4. Execute Docker**

```bash
$ docker-compose up -d
```

Output after executing:
- tile_creator/mapnik/mapnik.xml


# Errors

compiling Mapnik -> `SVG PARSING ERROR:"SVG support error: <enable-background> attribute is not supported"`

After ``python scripts/get-shapefiles.py -n -s`` on `tile_creator/start-up.sh` at container start.

```
...
tile_creator_1  | Warning: amenity-points.mss:2154:4 Styles do not match layer selector .text-low-zoom.
tile_creator_1  | Warning: amenity-points.mss:2140:4 Styles do not match layer selector .text-low-zoom.
tile_creator_1  | Warning: amenity-points.mss:2018:4 Styles do not match layer selector .text-low-zoom.
tile_creator_1  | Warning: amenity-points.mss:2003:4 Styles do not match layer selector .text-low-zoom.
tile_creator_1  | Warning: amenity-points.mss:1952:4 Styles do not match layer selector .text-low-zoom.
tile_creator_1  | Warning: amenity-points.mss:1927:4 Styles do not match layer selector .text-low-zoom.
tile_creator_1  | Warning: amenity-points.mss:1901:4 Styles do not match layer selector .text-low-zoom.
tile_creator_1  | Warning: amenity-points.mss:1852:4 Styles do not match layer selector .text-low-zoom.
tile_creator_1  | Warning: amenity-points.mss:1835:4 Styles do not match layer selector .text-low-zoom.
tile_creator_1  | Warning: amenity-points.mss:1822:4 Styles do not match layer selector .text-low-zoom.
tile_creator_1  | Warning: amenity-points.mss:1804:6 Styles do not match layer selector .text-low-zoom.
tile_creator_1  | Warning: amenity-points.mss:1780:4 Styles do not match layer selector .text-low-zoom.
tile_creator_1  | Warning: admin.mss:115:6 Styles do not match layer selector #admin-low-zoom.
```
