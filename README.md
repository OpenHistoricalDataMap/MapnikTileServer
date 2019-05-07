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


# ToDo's

Execute `indexes.sql` to database -> https://github.com/gravitystorm/openstreetmap-carto/blob/master/INSTALL.md#custom-indexes

install instructions -> https://ircama.github.io/osm-carto-tutorials/tile-server-ubuntu/

setup tileserver -> https://wiki.openstreetmap.org/wiki/Mod_tile/Setup_of_your_own_tile_server

# Errors

compiling Mapnik -> `SVG PARSING ERROR:"SVG support error: <enable-background> attribute is not supported"`

