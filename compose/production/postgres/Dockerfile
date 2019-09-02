# https://github.com/kartoza/docker-postgis
# PostgreSQL 11.0, PostGIS 2.5
FROM kartoza/postgis:11.0-2.5

COPY ./compose/production/postgres/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance

COPY ./compose/production/postgres/sql/ohdm.sql /docker-entrypoint-initdb.d/ohdm.sql
