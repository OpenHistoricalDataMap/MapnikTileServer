# OHDM-Docker

[![Documentation Status](https://readthedocs.org/projects/docker-ohdm/badge/?version=latest)](https://docker-ohdm.readthedocs.io/en/latest/?badge=latest)
     
It's a `docker-compose` repo for the new version of http://www.ohdm.net/, but it's just the beginning, so
do what you want and get back later :)

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
