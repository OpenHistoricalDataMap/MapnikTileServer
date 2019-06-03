# OHDM-Docker

[![Documentation Status](https://readthedocs.org/projects/docker-ohdm/badge/?version=latest)](https://docker-ohdm.readthedocs.io/en/latest/?badge=latest)
     
It's a `docker-compose` repo for the new version of http://www.ohdm.net/, but it's just the beginning, so
do what you want and get back later :)

![Docker Container Overview](docs/_static/ProjectOverview.png)

## minimum Server Requirements for developing

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
