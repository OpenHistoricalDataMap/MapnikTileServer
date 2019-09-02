import uuid
from datetime import date

from celery.result import AsyncResult
from django.contrib.gis.geos import Polygon
from django.db import models
from django.contrib.gis.db import models
from django.core.cache import cache

from ohdm_django_mapnik.ohdm.tile import TileGenerator


class TileCache(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    zoom = models.IntegerField()
    x_pixel = models.FloatField()
    y_pixel = models.FloatField()
    valid_since = models.DateField()
    valid_until = models.DateField()
    celery_task_id = models.CharField(blank=True, max_length=256)
    celery_task_done = models.BooleanField(default=False)

    def get_cache_key(self) -> str:
        return "t{}".format(self.pk)

    def get_tile_from_cache_or_delete(self):
        if not self.celery_task_done:
            tile_process: AsyncResult = AsyncResult(id=self.celery_task_id)
            while tile_process.ready() is False:
                pass

        tile = cache.get(self.get_cache_key())
        if tile is None:
            self.delete()
            return None
        else:
            return tile

    def set_valid_date(self):
        tile_generator: TileGenerator = TileGenerator(
            zoom=self.zoom,
            x_pixel=self.x_pixel,
            y_pixel=self.y_pixel
        )
        geom = Polygon.from_bbox(tile_generator.get_bbox())

        valid_since: date = self.valid_since
        valid_until: date = self.valid_until
        self.valid_since = None
        self.valid_until = None

        self.set_valid_date_iterate_objects(PlanetOsmLine.objects.filter(
            way__bbcontains=geom, valid_since__lte=valid_since, valid_until__gte=valid_until
        ))
        self.set_valid_date_iterate_objects(PlanetOsmPoint.objects.filter(
            way__bbcontains=geom, valid_since__lte=valid_since, valid_until__gte=valid_until
        ))
        self.set_valid_date_iterate_objects(PlanetOsmPolygon.objects.filter(
            way__bbcontains=geom, valid_since__lte=valid_since, valid_until__gte=valid_until
        ))
        self.set_valid_date_iterate_objects(PlanetOsmRoads.objects.filter(
            way__bbcontains=geom, valid_since__lte=valid_since, valid_until__gte=valid_until
        ))

        if self.valid_since is None:
            self.valid_since = valid_since
        if self.valid_until is None:
            self.valid_until = valid_until

        self.save()

    def set_valid_date_iterate_objects(self, lines: []):
        for line in lines:
            # valid_since
            if not self.valid_since:
                self.valid_since = line.valid_since
            else:
                if line.valid_since > self.valid_since:
                    self.valid_since = line.valid_since

            # valid_until
            if not self.valid_until:
                self.valid_until = line.valid_until
            else:
                if line.valid_until < self.valid_until:
                    self.valid_until = line.valid_until


class PlanetOsmLine(models.Model):
    osm_id = models.BigIntegerField(primary_key=True)
    access = models.TextField(blank=True, null=True)
    addr_housename = models.TextField(db_column='addr:housename', blank=True, null=True)
    addr_housenumber = models.TextField(db_column='addr:housenumber', blank=True, null=True)
    addr_interpolation = models.TextField(db_column='addr:interpolation', blank=True, null=True)
    admin_level = models.TextField(blank=True, null=True)
    aerialway = models.TextField(blank=True, null=True)
    aeroway = models.TextField(blank=True, null=True)
    amenity = models.TextField(blank=True, null=True)
    barrier = models.TextField(blank=True, null=True)
    bicycle = models.TextField(blank=True, null=True)
    bridge = models.TextField(blank=True, null=True)
    boundary = models.TextField(blank=True, null=True)
    building = models.TextField(blank=True, null=True)
    construction = models.TextField(blank=True, null=True)
    covered = models.TextField(blank=True, null=True)
    foot = models.TextField(blank=True, null=True)
    highway = models.TextField(blank=True, null=True)
    historic = models.TextField(blank=True, null=True)
    horse = models.TextField(blank=True, null=True)
    junction = models.TextField(blank=True, null=True)
    landuse = models.TextField(blank=True, null=True)
    layer = models.IntegerField(blank=True, null=True)
    leisure = models.TextField(blank=True, null=True)
    lock = models.TextField(blank=True, null=True)
    man_made = models.TextField(blank=True, null=True)
    military = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    natural = models.TextField(blank=True, null=True)
    oneway = models.TextField(blank=True, null=True)
    place = models.TextField(blank=True, null=True)
    power = models.TextField(blank=True, null=True)
    railway = models.TextField(blank=True, null=True)
    ref = models.TextField(blank=True, null=True)
    religion = models.TextField(blank=True, null=True)
    route = models.TextField(blank=True, null=True)
    service = models.TextField(blank=True, null=True)
    shop = models.TextField(blank=True, null=True)
    surface = models.TextField(blank=True, null=True)
    tourism = models.TextField(blank=True, null=True)
    tracktype = models.TextField(blank=True, null=True)
    tunnel = models.TextField(blank=True, null=True)
    water = models.TextField(blank=True, null=True)
    waterway = models.TextField(blank=True, null=True)
    way_area = models.FloatField(blank=True, null=True)
    z_order = models.IntegerField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    way = models.LineStringField(srid=3857, blank=True, null=True)
    valid_since = models.DateField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'planet_osm_line'


class PlanetOsmPoint(models.Model):
    osm_id = models.BigIntegerField(primary_key=True)
    access = models.TextField(blank=True, null=True)
    addr_housename = models.TextField(db_column='addr:housename', blank=True, null=True)
    addr_housenumber = models.TextField(db_column='addr:housenumber', blank=True, null=True)
    admin_level = models.TextField(blank=True, null=True)
    aerialway = models.TextField(blank=True, null=True)
    aeroway = models.TextField(blank=True, null=True)
    amenity = models.TextField(blank=True, null=True)
    barrier = models.TextField(blank=True, null=True)
    boundary = models.TextField(blank=True, null=True)
    building = models.TextField(blank=True, null=True)
    highway = models.TextField(blank=True, null=True)
    historic = models.TextField(blank=True, null=True)
    junction = models.TextField(blank=True, null=True)
    landuse = models.TextField(blank=True, null=True)
    layer = models.IntegerField(blank=True, null=True)
    leisure = models.TextField(blank=True, null=True)
    lock = models.TextField(blank=True, null=True)
    man_made = models.TextField(blank=True, null=True)
    military = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    natural = models.TextField(blank=True, null=True)
    oneway = models.TextField(blank=True, null=True)
    place = models.TextField(blank=True, null=True)
    power = models.TextField(blank=True, null=True)
    railway = models.TextField(blank=True, null=True)
    ref = models.TextField(blank=True, null=True)
    religion = models.TextField(blank=True, null=True)
    shop = models.TextField(blank=True, null=True)
    tourism = models.TextField(blank=True, null=True)
    water = models.TextField(blank=True, null=True)
    waterway = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    way = models.PointField(srid=3857, blank=True, null=True)
    valid_since = models.DateField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'planet_osm_point'


class PlanetOsmPolygon(models.Model):
    osm_id = models.BigIntegerField(primary_key=True)
    access = models.TextField(blank=True, null=True)
    addr_housename = models.TextField(db_column='addr:housename', blank=True, null=True)
    addr_housenumber = models.TextField(db_column='addr:housenumber', blank=True, null=True)
    addr_interpolation = models.TextField(db_column='addr:interpolation', blank=True, null=True)
    admin_level = models.TextField(blank=True, null=True)
    aerialway = models.TextField(blank=True, null=True)
    aeroway = models.TextField(blank=True, null=True)
    amenity = models.TextField(blank=True, null=True)
    barrier = models.TextField(blank=True, null=True)
    bicycle = models.TextField(blank=True, null=True)
    bridge = models.TextField(blank=True, null=True)
    boundary = models.TextField(blank=True, null=True)
    building = models.TextField(blank=True, null=True)
    construction = models.TextField(blank=True, null=True)
    covered = models.TextField(blank=True, null=True)
    foot = models.TextField(blank=True, null=True)
    highway = models.TextField(blank=True, null=True)
    historic = models.TextField(blank=True, null=True)
    horse = models.TextField(blank=True, null=True)
    junction = models.TextField(blank=True, null=True)
    landuse = models.TextField(blank=True, null=True)
    layer = models.IntegerField(blank=True, null=True)
    leisure = models.TextField(blank=True, null=True)
    lock = models.TextField(blank=True, null=True)
    man_made = models.TextField(blank=True, null=True)
    military = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    natural = models.TextField(blank=True, null=True)
    oneway = models.TextField(blank=True, null=True)
    place = models.TextField(blank=True, null=True)
    power = models.TextField(blank=True, null=True)
    railway = models.TextField(blank=True, null=True)
    ref = models.TextField(blank=True, null=True)
    religion = models.TextField(blank=True, null=True)
    route = models.TextField(blank=True, null=True)
    service = models.TextField(blank=True, null=True)
    shop = models.TextField(blank=True, null=True)
    surface = models.TextField(blank=True, null=True)
    tourism = models.TextField(blank=True, null=True)
    tracktype = models.TextField(blank=True, null=True)
    tunnel = models.TextField(blank=True, null=True)
    water = models.TextField(blank=True, null=True)
    waterway = models.TextField(blank=True, null=True)
    way_area = models.FloatField(blank=True, null=True)
    z_order = models.IntegerField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    way = models.GeometryField(srid=3857, blank=True, null=True)
    valid_since = models.DateField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'planet_osm_polygon'


class PlanetOsmRoads(models.Model):
    osm_id = models.BigIntegerField(primary_key=True)
    access = models.TextField(blank=True, null=True)
    addr_housename = models.TextField(db_column='addr:housename', blank=True, null=True)
    addr_housenumber = models.TextField(db_column='addr:housenumber', blank=True, null=True)
    addr_interpolation = models.TextField(db_column='addr:interpolation', blank=True, null=True)
    admin_level = models.TextField(blank=True, null=True)
    aerialway = models.TextField(blank=True, null=True)
    aeroway = models.TextField(blank=True, null=True)
    amenity = models.TextField(blank=True, null=True)
    barrier = models.TextField(blank=True, null=True)
    bicycle = models.TextField(blank=True, null=True)
    bridge = models.TextField(blank=True, null=True)
    boundary = models.TextField(blank=True, null=True)
    building = models.TextField(blank=True, null=True)
    construction = models.TextField(blank=True, null=True)
    covered = models.TextField(blank=True, null=True)
    foot = models.TextField(blank=True, null=True)
    highway = models.TextField(blank=True, null=True)
    historic = models.TextField(blank=True, null=True)
    horse = models.TextField(blank=True, null=True)
    junction = models.TextField(blank=True, null=True)
    landuse = models.TextField(blank=True, null=True)
    layer = models.IntegerField(blank=True, null=True)
    leisure = models.TextField(blank=True, null=True)
    lock = models.TextField(blank=True, null=True)
    man_made = models.TextField(blank=True, null=True)
    military = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    natural = models.TextField(blank=True, null=True)
    oneway = models.TextField(blank=True, null=True)
    place = models.TextField(blank=True, null=True)
    power = models.TextField(blank=True, null=True)
    railway = models.TextField(blank=True, null=True)
    ref = models.TextField(blank=True, null=True)
    religion = models.TextField(blank=True, null=True)
    route = models.TextField(blank=True, null=True)
    service = models.TextField(blank=True, null=True)
    shop = models.TextField(blank=True, null=True)
    surface = models.TextField(blank=True, null=True)
    tourism = models.TextField(blank=True, null=True)
    tracktype = models.TextField(blank=True, null=True)
    tunnel = models.TextField(blank=True, null=True)
    water = models.TextField(blank=True, null=True)
    waterway = models.TextField(blank=True, null=True)
    way_area = models.FloatField(blank=True, null=True)
    z_order = models.IntegerField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    way = models.LineStringField(srid=3857, blank=True, null=True)
    valid_since = models.DateField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'planet_osm_roads'
