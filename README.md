# OHDM Mapnik Tile Server

![https://github.com/OpenHistoricalDataMap/MapnikTileServer/wiki](https://img.shields.io/badge/wiki-read-green.svg)
![https://github.com/OpenHistoricalDataMap/MapnikTileServer/wiki/Setup](https://img.shields.io/badge/Docker--Compose-ready-green.svg)

A time sensitive [Mapnik](https://mapnik.org/) Tile Server written in Python with [Flask Framework](http://flask.pocoo.org/).

![Docker Container Overview](https://raw.githubusercontent.com/wiki/OpenHistoricalDataMap/MapnikTileServer/_static/ProjectOverview.png)

![Docker Container Overview](docs/_static/ProjectOverview.png)

```
OHDM
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
│   └───code
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

**2. Import**

TODO 

**3. Create docker network** `web`

```bash
$ docker network create web
```

**4. Build Docker Image**

```bash
$ docker-compose build
```

**5. Execute Docker**

```bash
$ docker-compose up -d webserver
```
