/* add valid columns */

/* planet_osm_line */
alter table planet_osm_line
    add valid_since date;

alter table planet_osm_line
    add valid_until date;

/* planet_osm_point */
alter table planet_osm_point
    add valid_since date;

alter table planet_osm_point
    add valid_until date;

/* planet_osm_polygon */
alter table planet_osm_polygon
    add valid_since date;

alter table planet_osm_polygon
    add valid_until date;

/* planet_osm_roads */
alter table planet_osm_roads
    add valid_since date;

alter table planet_osm_roads
    add valid_until date;


/* add default value in valid columns */

/* planet_osm_line */
UPDATE planet_osm_line
SET valid_since = '2008-11-11',
    valid_until = '2019-01-01';

/* planet_osm_point */
UPDATE planet_osm_point
SET valid_since = '2008-11-11',
    valid_until = '2019-01-01';

/* planet_osm_polygon */
UPDATE planet_osm_polygon
SET valid_since = '2008-11-11',
    valid_until = '2019-01-01';

/* planet_osm_roads */
UPDATE planet_osm_roads
SET valid_since = '2008-11-11',
    valid_until = '2019-01-01';
