# https://github.com/kartoza/docker-postgis
# PostgreSQL 12.0, PostGIS 3
FROM kartoza/postgis:12.1

COPY ./compose/production/postgres/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance
