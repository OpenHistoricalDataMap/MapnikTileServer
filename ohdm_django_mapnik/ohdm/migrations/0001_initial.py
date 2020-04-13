# Generated by Django 3.0.3 on 2020-04-13 07:27

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields
import django.contrib.postgres.fields.hstore
from django.contrib.postgres.operations import HStoreExtension
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        HStoreExtension(),
        migrations.CreateModel(
            name='Classification',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('class_field', models.CharField(blank=True, db_column='class', max_length=255, null=True)),
                ('subclassname', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'classification',
            },
        ),
        migrations.CreateModel(
            name='Geoobject',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('source_user_id', models.BigIntegerField()),
            ],
            options={
                'db_table': 'geoobject',
            },
        ),
        migrations.CreateModel(
            name='GeoobjectGeometry',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('id_target', models.BigIntegerField(blank=True, null=True)),
                ('type_target', models.IntegerField(blank=True, null=True)),
                ('id_geoobject_source', models.BigIntegerField()),
                ('role', models.CharField(blank=True, max_length=255, null=True)),
                ('classification_id', models.BigIntegerField()),
                ('tags', models.TextField(blank=True, null=True)),
                ('valid_since', models.DateField()),
                ('valid_until', models.DateField()),
                ('valid_since_offset', models.BigIntegerField(blank=True, null=True)),
                ('valid_until_offset', models.BigIntegerField(blank=True, null=True)),
                ('source_user_id', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'geoobject_geometry',
            },
        ),
        migrations.CreateModel(
            name='Lines',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('line', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=0)),
                ('source_user_id', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'lines',
            },
        ),
        migrations.CreateModel(
            name='OhdmGeoobjectWay',
            fields=[
                ('way_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('geoobject_id', models.BigIntegerField()),
                ('name', models.CharField(max_length=255)),
                ('role', models.CharField(max_length=255)),
                ('classification_class', models.CharField(max_length=255)),
                ('classification_subclassname', models.CharField(max_length=255)),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField()),
                ('valid_since', models.DateField()),
                ('valid_until', models.DateField()),
                ('way', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='PlanetOsmLine',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('osm_id', models.BigIntegerField(blank=True, null=True)),
                ('version', models.IntegerField(blank=True, null=True)),
                ('visible', models.BooleanField(blank=True, null=True)),
                ('geoobject', models.BigIntegerField(blank=True, null=True)),
                ('access', models.TextField(blank=True, null=True)),
                ('addr_housename', models.TextField(blank=True, db_column='addr:housename', null=True)),
                ('addr_housenumber', models.TextField(blank=True, db_column='addr:housenumber', null=True)),
                ('addr_interpolation', models.TextField(blank=True, db_column='addr:interpolation', null=True)),
                ('admin_level', models.TextField(blank=True, null=True)),
                ('aerialway', models.TextField(blank=True, null=True)),
                ('aeroway', models.TextField(blank=True, null=True)),
                ('amenity', models.TextField(blank=True, null=True)),
                ('barrier', models.TextField(blank=True, null=True)),
                ('bicycle', models.TextField(blank=True, null=True)),
                ('bridge', models.TextField(blank=True, null=True)),
                ('boundary', models.TextField(blank=True, null=True)),
                ('building', models.TextField(blank=True, null=True)),
                ('construction', models.TextField(blank=True, null=True)),
                ('covered', models.TextField(blank=True, null=True)),
                ('foot', models.TextField(blank=True, null=True)),
                ('highway', models.TextField(blank=True, null=True)),
                ('historic', models.TextField(blank=True, null=True)),
                ('horse', models.TextField(blank=True, null=True)),
                ('junction', models.TextField(blank=True, null=True)),
                ('landuse', models.TextField(blank=True, null=True)),
                ('layer', models.IntegerField(blank=True, null=True)),
                ('leisure', models.TextField(blank=True, null=True)),
                ('lock', models.TextField(blank=True, null=True)),
                ('man_made', models.TextField(blank=True, null=True)),
                ('military', models.TextField(blank=True, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('natural', models.TextField(blank=True, null=True)),
                ('oneway', models.TextField(blank=True, null=True)),
                ('place', models.TextField(blank=True, null=True)),
                ('power', models.TextField(blank=True, null=True)),
                ('railway', models.TextField(blank=True, null=True)),
                ('ref', models.TextField(blank=True, null=True)),
                ('religion', models.TextField(blank=True, null=True)),
                ('route', models.TextField(blank=True, null=True)),
                ('service', models.TextField(blank=True, null=True)),
                ('shop', models.TextField(blank=True, null=True)),
                ('surface', models.TextField(blank=True, null=True)),
                ('tourism', models.TextField(blank=True, null=True)),
                ('tracktype', models.TextField(blank=True, null=True)),
                ('tunnel', models.TextField(blank=True, null=True)),
                ('water', models.TextField(blank=True, null=True)),
                ('waterway', models.TextField(blank=True, null=True)),
                ('way_area', models.FloatField(blank=True, null=True)),
                ('z_order', models.IntegerField(blank=True, null=True)),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField(default=dict)),
                ('way', django.contrib.gis.db.models.fields.LineStringField(blank=True, null=True, srid=3857)),
                ('valid_since', models.DateField(blank=True, null=True)),
                ('valid_until', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'planet_osm_line',
            },
        ),
        migrations.CreateModel(
            name='PlanetOsmNodes',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('osm_id', models.BigIntegerField()),
                ('version', models.IntegerField()),
                ('visible', models.BooleanField()),
                ('point', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=3857)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField(default=dict)),
            ],
            options={
                'db_table': 'planet_osm_nodes',
            },
        ),
        migrations.CreateModel(
            name='PlanetOsmPoint',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('osm_id', models.BigIntegerField(blank=True, null=True)),
                ('version', models.IntegerField(blank=True, null=True)),
                ('visible', models.BooleanField(blank=True, null=True)),
                ('geoobject', models.BigIntegerField(blank=True, null=True)),
                ('access', models.TextField(blank=True, null=True)),
                ('addr_housename', models.TextField(blank=True, db_column='addr:housename', null=True)),
                ('addr_housenumber', models.TextField(blank=True, db_column='addr:housenumber', null=True)),
                ('admin_level', models.TextField(blank=True, null=True)),
                ('aerialway', models.TextField(blank=True, null=True)),
                ('aeroway', models.TextField(blank=True, null=True)),
                ('amenity', models.TextField(blank=True, null=True)),
                ('barrier', models.TextField(blank=True, null=True)),
                ('boundary', models.TextField(blank=True, null=True)),
                ('building', models.TextField(blank=True, null=True)),
                ('highway', models.TextField(blank=True, null=True)),
                ('historic', models.TextField(blank=True, null=True)),
                ('junction', models.TextField(blank=True, null=True)),
                ('landuse', models.TextField(blank=True, null=True)),
                ('layer', models.IntegerField(blank=True, null=True)),
                ('leisure', models.TextField(blank=True, null=True)),
                ('lock', models.TextField(blank=True, null=True)),
                ('man_made', models.TextField(blank=True, null=True)),
                ('military', models.TextField(blank=True, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('natural', models.TextField(blank=True, null=True)),
                ('oneway', models.TextField(blank=True, null=True)),
                ('place', models.TextField(blank=True, null=True)),
                ('power', models.TextField(blank=True, null=True)),
                ('railway', models.TextField(blank=True, null=True)),
                ('ref', models.TextField(blank=True, null=True)),
                ('religion', models.TextField(blank=True, null=True)),
                ('shop', models.TextField(blank=True, null=True)),
                ('tourism', models.TextField(blank=True, null=True)),
                ('water', models.TextField(blank=True, null=True)),
                ('waterway', models.TextField(blank=True, null=True)),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField(default=dict)),
                ('way', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=3857)),
                ('valid_since', models.DateField(blank=True, null=True)),
                ('valid_until', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'planet_osm_point',
            },
        ),
        migrations.CreateModel(
            name='PlanetOsmPolygon',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('osm_id', models.BigIntegerField(blank=True, null=True)),
                ('version', models.IntegerField(blank=True, null=True)),
                ('visible', models.BooleanField(blank=True, null=True)),
                ('geoobject', models.BigIntegerField(blank=True, null=True)),
                ('access', models.TextField(blank=True, null=True)),
                ('addr_housename', models.TextField(blank=True, db_column='addr:housename', null=True)),
                ('addr_housenumber', models.TextField(blank=True, db_column='addr:housenumber', null=True)),
                ('addr_interpolation', models.TextField(blank=True, db_column='addr:interpolation', null=True)),
                ('admin_level', models.TextField(blank=True, null=True)),
                ('aerialway', models.TextField(blank=True, null=True)),
                ('aeroway', models.TextField(blank=True, null=True)),
                ('amenity', models.TextField(blank=True, null=True)),
                ('barrier', models.TextField(blank=True, null=True)),
                ('bicycle', models.TextField(blank=True, null=True)),
                ('bridge', models.TextField(blank=True, null=True)),
                ('boundary', models.TextField(blank=True, null=True)),
                ('building', models.TextField(blank=True, null=True)),
                ('construction', models.TextField(blank=True, null=True)),
                ('covered', models.TextField(blank=True, null=True)),
                ('foot', models.TextField(blank=True, null=True)),
                ('highway', models.TextField(blank=True, null=True)),
                ('historic', models.TextField(blank=True, null=True)),
                ('horse', models.TextField(blank=True, null=True)),
                ('junction', models.TextField(blank=True, null=True)),
                ('landuse', models.TextField(blank=True, null=True)),
                ('layer', models.IntegerField(blank=True, null=True)),
                ('leisure', models.TextField(blank=True, null=True)),
                ('lock', models.TextField(blank=True, null=True)),
                ('man_made', models.TextField(blank=True, null=True)),
                ('military', models.TextField(blank=True, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('natural', models.TextField(blank=True, null=True)),
                ('oneway', models.TextField(blank=True, null=True)),
                ('place', models.TextField(blank=True, null=True)),
                ('power', models.TextField(blank=True, null=True)),
                ('railway', models.TextField(blank=True, null=True)),
                ('ref', models.TextField(blank=True, null=True)),
                ('religion', models.TextField(blank=True, null=True)),
                ('route', models.TextField(blank=True, null=True)),
                ('service', models.TextField(blank=True, null=True)),
                ('shop', models.TextField(blank=True, null=True)),
                ('surface', models.TextField(blank=True, null=True)),
                ('tourism', models.TextField(blank=True, null=True)),
                ('tracktype', models.TextField(blank=True, null=True)),
                ('tunnel', models.TextField(blank=True, null=True)),
                ('water', models.TextField(blank=True, null=True)),
                ('waterway', models.TextField(blank=True, null=True)),
                ('way_area', models.FloatField(blank=True, null=True)),
                ('z_order', models.IntegerField(blank=True, null=True)),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField(default=dict)),
                ('way', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=3857)),
                ('valid_since', models.DateField(blank=True, null=True)),
                ('valid_until', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'planet_osm_polygon',
            },
        ),
        migrations.CreateModel(
            name='PlanetOsmRels',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('osm_id', models.BigIntegerField()),
                ('version', models.IntegerField()),
                ('visible', models.BooleanField()),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField(default=dict)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('inner_members', django.contrib.postgres.fields.ArrayField(base_field=models.BigIntegerField(), blank=True, null=True, size=None)),
                ('outer_members', django.contrib.postgres.fields.ArrayField(base_field=models.BigIntegerField(), blank=True, null=True, size=None)),
                ('rel_type', models.CharField(blank=True, max_length=256, null=True)),
            ],
            options={
                'db_table': 'planet_osm_rels',
            },
        ),
        migrations.CreateModel(
            name='PlanetOsmRoads',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('osm_id', models.BigIntegerField(blank=True, null=True)),
                ('version', models.IntegerField(blank=True, null=True)),
                ('visible', models.BooleanField(blank=True, null=True)),
                ('geoobject', models.BigIntegerField(blank=True, null=True)),
                ('access', models.TextField(blank=True, null=True)),
                ('addr_housename', models.TextField(blank=True, db_column='addr:housename', null=True)),
                ('addr_housenumber', models.TextField(blank=True, db_column='addr:housenumber', null=True)),
                ('addr_interpolation', models.TextField(blank=True, db_column='addr:interpolation', null=True)),
                ('admin_level', models.TextField(blank=True, null=True)),
                ('aerialway', models.TextField(blank=True, null=True)),
                ('aeroway', models.TextField(blank=True, null=True)),
                ('amenity', models.TextField(blank=True, null=True)),
                ('barrier', models.TextField(blank=True, null=True)),
                ('bicycle', models.TextField(blank=True, null=True)),
                ('bridge', models.TextField(blank=True, null=True)),
                ('boundary', models.TextField(blank=True, null=True)),
                ('building', models.TextField(blank=True, null=True)),
                ('construction', models.TextField(blank=True, null=True)),
                ('covered', models.TextField(blank=True, null=True)),
                ('foot', models.TextField(blank=True, null=True)),
                ('highway', models.TextField(blank=True, null=True)),
                ('historic', models.TextField(blank=True, null=True)),
                ('horse', models.TextField(blank=True, null=True)),
                ('junction', models.TextField(blank=True, null=True)),
                ('landuse', models.TextField(blank=True, null=True)),
                ('layer', models.IntegerField(blank=True, null=True)),
                ('leisure', models.TextField(blank=True, null=True)),
                ('lock', models.TextField(blank=True, null=True)),
                ('man_made', models.TextField(blank=True, null=True)),
                ('military', models.TextField(blank=True, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('natural', models.TextField(blank=True, null=True)),
                ('oneway', models.TextField(blank=True, null=True)),
                ('place', models.TextField(blank=True, null=True)),
                ('power', models.TextField(blank=True, null=True)),
                ('railway', models.TextField(blank=True, null=True)),
                ('ref', models.TextField(blank=True, null=True)),
                ('religion', models.TextField(blank=True, null=True)),
                ('route', models.TextField(blank=True, null=True)),
                ('service', models.TextField(blank=True, null=True)),
                ('shop', models.TextField(blank=True, null=True)),
                ('surface', models.TextField(blank=True, null=True)),
                ('tourism', models.TextField(blank=True, null=True)),
                ('tracktype', models.TextField(blank=True, null=True)),
                ('tunnel', models.TextField(blank=True, null=True)),
                ('water', models.TextField(blank=True, null=True)),
                ('waterway', models.TextField(blank=True, null=True)),
                ('way_area', models.FloatField(blank=True, null=True)),
                ('z_order', models.IntegerField(blank=True, null=True)),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField(default=dict)),
                ('way', django.contrib.gis.db.models.fields.LineStringField(blank=True, null=True, srid=3857)),
                ('valid_since', models.DateField(blank=True, null=True)),
                ('valid_until', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'planet_osm_roads',
            },
        ),
        migrations.CreateModel(
            name='PlanetOsmWays',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('osm_id', models.BigIntegerField()),
                ('version', models.IntegerField()),
                ('visible', models.BooleanField()),
                ('way', django.contrib.gis.db.models.fields.LineStringField(blank=True, null=True, srid=3857)),
                ('timestamp', models.DateField(blank=True, null=True)),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField(default=dict)),
            ],
            options={
                'db_table': 'planet_osm_ways',
            },
        ),
        migrations.CreateModel(
            name='Points',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('point', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=0)),
                ('source_user_id', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'points',
            },
        ),
        migrations.CreateModel(
            name='Polygons',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('polygon', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=0)),
                ('source_user_id', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'polygons',
            },
        ),
        migrations.CreateModel(
            name='TileCache',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('zoom', models.IntegerField()),
                ('x_pixel', models.FloatField()),
                ('y_pixel', models.FloatField()),
                ('valid_since', models.DateField(null=True)),
                ('valid_until', models.DateField(null=True)),
                ('celery_task_id', models.CharField(blank=True, max_length=256)),
                ('celery_task_done', models.BooleanField(default=False)),
            ],
        ),
    ]
