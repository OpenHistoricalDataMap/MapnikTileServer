from __future__ import annotations

from datetime import date
from time import sleep
from typing import Any, List, Optional

from celery.result import AsyncResult
from django.contrib.gis.db import models
from django.contrib.gis.geos import Polygon
from django.contrib.postgres.fields import HStoreField
from django.core.cache import cache

from ohdm_django_mapnik.ohdm.tile import TileGenerator


class TileCache(models.Model):
    """
    Model for mapnik tile cache
    """

    created = models.DateTimeField(auto_now_add=True)
    zoom = models.IntegerField()
    x_pixel = models.FloatField()
    y_pixel = models.FloatField()
    valid_since = models.DateField(null=True)
    valid_until = models.DateField(null=True)
    celery_task_id = models.CharField(blank=True, max_length=256)
    celery_task_done = models.BooleanField(default=False)

    def get_cache_key(self) -> str:
        """
        get cache key

        Returns:
            str -- cache key to get the tile from the cache
        """
        return "t{}".format(self.pk)

    def get_tile_from_cache_or_delete(self) -> Optional[bytes]:
        """
        Get cached tile from the cache server, if the request cache does not
        exists -> delete the cache object from the database
        
        Returns:
            Optional[bytes] -- Tile PNG as bytes if exists
        """

        # wait to finish celery task
        if not self.celery_task_done:
            tile_process: AsyncResult = AsyncResult(id=self.celery_task_id)
            while tile_process.ready() is False:
                sleep(0.1)
                # todo add max wait time

        # get tile from cache as bytes PNG
        tile: Optional[bytes] = cache.get(self.get_cache_key())

        # if cache file does not exists -> delete TileCache
        if not tile:
            self.delete()

        # return tile as bytes PNG
        return tile

    def set_valid_date(self):
        tile_generator: TileGenerator = TileGenerator(
            zoom=self.zoom, x_pixel=self.x_pixel, y_pixel=self.y_pixel
        )
        geom = Polygon.from_bbox(tile_generator.get_bbox())

        valid_since: Optional[date] = self.valid_since
        valid_until: Optional[date] = self.valid_until
        self.valid_since = None
        self.valid_until = None

        planet_osm_lines: List[PlanetOsmLine] = []
        for planet_osm_line in PlanetOsmLine.objects.filter(
            way__bbcontains=geom,
            valid_since__lte=valid_since,
            valid_until__gte=valid_until,
        ):
            planet_osm_lines.append(planet_osm_line)
        self.set_valid_date_iterate_objects(planet_osm_lines)

        planet_osm_points: List[PlanetOsmPoint] = []
        for planet_osm_point in PlanetOsmPoint.objects.filter(
            way__bbcontains=geom,
            valid_since__lte=valid_since,
            valid_until__gte=valid_until,
        ):
            planet_osm_points.append(planet_osm_point)
        self.set_valid_date_iterate_objects(planet_osm_points)

        planet_osm_polygons: List[PlanetOsmPolygon] = []
        for planet_osm_polygon in PlanetOsmPolygon.objects.filter(
            way__bbcontains=geom,
            valid_since__lte=valid_since,
            valid_until__gte=valid_until,
        ):
            planet_osm_polygons.append(planet_osm_polygon)
        self.set_valid_date_iterate_objects(planet_osm_polygons)

        planet_osm_roadss: List[PlanetOsmRoads] = []
        for planet_osm_roads in PlanetOsmRoads.objects.filter(
            way__bbcontains=geom,
            valid_since__lte=valid_since,
            valid_until__gte=valid_until,
        ):
            planet_osm_roadss.append(planet_osm_roads)
        self.set_valid_date_iterate_objects(planet_osm_roadss)

        if self.valid_since is None:
            self.valid_since = valid_since
        if self.valid_until is None:
            self.valid_until = valid_until

        self.save()

    def set_valid_date_iterate_objects(self, lines: List[Any]):
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

    def delete(self, **kwargs):
        cache.delete(self.get_cache_key())
        super().delete()

    def __str__(self):
        if not self.valid_since:
            raise ValueError("valid_since are not set!")
        if not self.valid_until:
            raise ValueError("valid_until are not set!")
        return "{0}: {1}-{2} z:{3} x:{4} y:{5}".format(
            self.pk,
            self.valid_since.strftime("%Y/%m/%d"),
            self.valid_until.strftime("%Y/%m/%d"),
            self.zoom,
            self.x_pixel,
            self.y_pixel,
        )


class OhdmGeoobjectWay(models.Model):
    way_id = models.BigIntegerField(primary_key=True)
    geoobject_id = models.BigIntegerField()
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    classification_class = models.CharField(max_length=255)
    classification_subclassname = models.CharField(max_length=255)
    tags = HStoreField()
    valid_since = models.DateField()
    valid_until = models.DateField()
    way = models.TextField()

    class Meta:
        managed = False

    class GEOMETRY_TYPE:
        POINT = "point"
        LINE = "line"
        POLYGON = "polygon"

        TYPES = [POINT, LINE, POLYGON]


class PlanetOsmLine(models.Model):
    """
    osm line model
    """

    osm_id = models.BigIntegerField(blank=True, null=True)
    geoobject = models.BigIntegerField(blank=True, null=True)
    access = models.TextField(blank=True, null=True)
    addr_housename = models.TextField(db_column="addr:housename", blank=True, null=True)
    addr_housenumber = models.TextField(
        db_column="addr:housenumber", blank=True, null=True
    )
    addr_interpolation = models.TextField(
        db_column="addr:interpolation", blank=True, null=True
    )
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
    tags = HStoreField(blank=True, null=True)
    way = models.LineStringField(srid=3857, blank=True, null=True)
    valid_since = models.DateField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "planet_osm_line"


class PlanetOsmPoint(models.Model):
    """
    osm point model
    """

    osm_id = models.BigIntegerField(blank=True, null=True)
    geoobject = models.BigIntegerField(blank=True, null=True)
    access = models.TextField(blank=True, null=True)
    addr_housename = models.TextField(db_column="addr:housename", blank=True, null=True)
    addr_housenumber = models.TextField(
        db_column="addr:housenumber", blank=True, null=True
    )
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
    tags = HStoreField(blank=True, null=True)
    way = models.PointField(srid=3857, blank=True, null=True)
    valid_since = models.DateField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "planet_osm_point"


class PlanetOsmPolygon(models.Model):
    """
    osm polygon model
    """

    osm_id = models.BigIntegerField(blank=True, null=True)
    geoobject = models.BigIntegerField(blank=True, null=True)
    access = models.TextField(blank=True, null=True)
    addr_housename = models.TextField(db_column="addr:housename", blank=True, null=True)
    addr_housenumber = models.TextField(
        db_column="addr:housenumber", blank=True, null=True
    )
    addr_interpolation = models.TextField(
        db_column="addr:interpolation", blank=True, null=True
    )
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
    tags = HStoreField(blank=True, null=True)
    way = models.GeometryField(srid=3857, blank=True, null=True)
    valid_since = models.DateField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "planet_osm_polygon"


class PlanetOsmRoads(models.Model):
    """
    osm road model
    """

    osm_id = models.BigIntegerField(blank=True, null=True)
    geoobject = models.BigIntegerField(blank=True, null=True)
    access = models.TextField(blank=True, null=True)
    addr_housename = models.TextField(db_column="addr:housename", blank=True, null=True)
    addr_housenumber = models.TextField(
        db_column="addr:housenumber", blank=True, null=True
    )
    addr_interpolation = models.TextField(
        db_column="addr:interpolation", blank=True, null=True
    )
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
        db_table = "planet_osm_roads"
