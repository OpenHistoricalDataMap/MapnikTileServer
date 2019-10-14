# OHDM Mapnik Tile Server

![https://github.com/OpenHistoricalDataMap/MapnikTileServer/wiki](https://img.shields.io/badge/wiki-read-green.svg)
![https://github.com/OpenHistoricalDataMap/MapnikTileServer/wiki/Setup](https://img.shields.io/badge/Docker--Compose-ready-green.svg)

A time sensitive [Mapnik](https://mapnik.org/) Tile Server written in Python with [Flask Framework](http://flask.pocoo.org/).

![Docker Container Overview](https://raw.githubusercontent.com/wiki/OpenHistoricalDataMap/MapnikTileServer/_static/ProjectOverview.png)

```
OHDM Mapnik Tile Server
│   .env                               # enviroment var file
│   .env-example                       # example enviroment var file
│   .gitignore
│   .readthedocs.yml                   # config file for https://readthedocs.org/
│   docker-compose.yml                 # docker-compose file
│   LICENSE 
│   project.mml                        # mapnik style, edit only for develop / testing purpose
│   README.md  
│    
└───docs                               # docs based on https://readthedocs.org/
│
└───import                             # dockerfile & startup script to import database
│
└───nginx                              # nginx conf files
│
└───proxy                              # traefik conf files
│
└───tile_server                        # wordpress files
│   │   dockerfile                     # tile_server dockerfile
│   │   requirements.txt               # python dependencies for the tile server
|   |   date_template_importer.py      # script for inserting date template into Mapnik style conf file
│   └───app
│       │   __init__.py
│       │   app.py                     # tile server code (flask & mapnik)
│       │   wsgi.py                    # start script for the production server
│
└───website                            # html content of demo OHDM website
```

## minimum Server Requirements for developing

- 3 GB of RAM
- 20 GB of free disk space

## Quickstart

**1. create** `.env`

Copy `.env-example` to `.env` and change it to you needs

If you need more explanation about the `.env` file, look in the docs -> https://readthedocs.org/projects/docker-ohdm/

```bash
$ cp .env-example .env
$ vim .env
```

**2. Import (Import Demo Database - Optional)**

Download a OSM Datafile like https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf into ``./pbf``

```bash
$ wget https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf -P pbf
$ docker-compose up import
```

**3. Create docker network** `web`

```bash
$ docker network create web
```

**4. Build Docker Image**

```bash
$ docker-compose build
```

**5. Execute Docker**

To start the tile server with a Docker Database Server

```bash
$ docker-compose up -d webserver postgis
```

To start the tile server with a external Database Server

```bash
$ docker-compose up -d webserver
```
