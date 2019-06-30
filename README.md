# OHDM Mapnik Tile Server

![https://github.com/OpenHistoricalDataMap/MapnikTileServer/wiki](https://img.shields.io/badge/wiki-read-green.svg)
![https://github.com/OpenHistoricalDataMap/MapnikTileServer/wiki/Setup](https://img.shields.io/badge/Docker--Compose-ready-green.svg)

A time sensitive [Mapnik](https://mapnik.org/) Tile Server written in Python with [Flask Framework](http://flask.pocoo.org/).

![Docker Container Overview](https://raw.githubusercontent.com/wiki/OpenHistoricalDataMap/MapnikTileServer/_static/ProjectOverview.png)

## minimum Server Requirements

- 3 GB of RAM
- 20 GB of free disk space

## Quickstart

**1. create** `.env`

Copy `.env-example` to `.env` and change it to you needs

-> todo need more description

```bash
$ cp .env-example .env
$ vim .env
```

**2. Download a** `*.pbf` **file to** `./pbf`

```bash
$ wget https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf -O pbf/berlin-latest.osm.pbf
```

**3. Create docker network** `web`

```bash
$ docker network create web
```

**4. Build Docker Image**

```bash
$ docker-compose build
```

**5. all files from `./pbf/` to database**

```bash
$ docker-compose up -d postgis
```

**6. Execute Docker**

```bash
$ docker-compose up -d
```
