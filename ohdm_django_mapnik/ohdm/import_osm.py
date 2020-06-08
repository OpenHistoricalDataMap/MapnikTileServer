import logging
from datetime import datetime
from typing import List

from django.contrib.gis.gdal import CoordTransform, SpatialReference
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.utils import timezone
from osmium import SimpleHandler
from osmium.geom import WKTFactory
from osmium.osm._osm import Area, Node, TagList, Way

from .models import (PlanetOsmLine, PlanetOsmPoint, PlanetOsmPolygon,
                     PlanetOsmRoads)
from .postgis_utily import set_polygon_way_area
from .tags2mapnik import cleanup_tags, fill_osm_object, get_z_order, is_road

logger = logging.getLogger(__name__)


class OSMHandler(SimpleHandler):
    def __init__(self, db_cache_size: int):
        SimpleHandler.__init__(self)

        # A global factory that creates WKB from a osmium geometry
        self.wkt_fab: WKTFactory = WKTFactory()

        # https://docs.djangoproject.com/en/3.0/ref/contrib/gis/gdal/#coordtransform
        self.ct: CoordTransform = CoordTransform(
            SpatialReference(self.wkt_fab.epsg), SpatialReference(3857)
        )

        self.point_cache: List[PlanetOsmPoint] = []
        self.line_cache: List[PlanetOsmLine] = []
        self.roads_cache: List[PlanetOsmRoads] = []
        self.polygon_cache: List[PlanetOsmPolygon] = []

        self.node_counter: int = 0
        self.way_counter: int = 0
        self.area_counter: int = 0

        self.db_cache_size: int = db_cache_size

        self.valid_until: datetime = timezone.now()

        logger.info("starting import ...")

    def show_import_status(self):
        """
        Show import status every 10000 entries
        """
        if (self.node_counter + self.way_counter + self.area_counter) % 10000 == 0:
            logger.info(
                "Nodes: {} | Ways: {} | Area: {}".format(
                    self.node_counter, self.way_counter, self.area_counter
                )
            )

    def check_cache_save(self):
        """
        Check if chuck_size is succeed & save cached geo-objects
        """
        if (
            self.node_counter + self.way_counter + self.area_counter
        ) % self.db_cache_size == 0:
            self.save_cache()

    def count_node(self):
        """
        Count Node, check for save cache & show import status
        """
        self.node_counter += 1
        self.check_cache_save()

        self.show_import_status()

    def count_way(self):
        """
        Count Way, check for save cache & show import status
        """
        self.way_counter += 1
        self.check_cache_save()

        self.show_import_status()

    def count_area(self):
        """
        Count Area, check for save cache & show import status
        """
        self.area_counter += 1
        self.check_cache_save()

        self.show_import_status()

    def save_cache(self):
        """
        Save cached geo-objects into database & clear cache
        """
        logger.info("saving cache ...")
        if self.point_cache:
            PlanetOsmPoint.objects.bulk_create(self.point_cache)
            self.point_cache.clear()
        if self.line_cache:
            PlanetOsmLine.objects.bulk_create(self.line_cache)
            self.line_cache.clear()
        if self.roads_cache:
            PlanetOsmRoads.objects.bulk_create(self.roads_cache)
            self.roads_cache.clear()
        if self.polygon_cache:
            PlanetOsmPolygon.objects.bulk_create(self.polygon_cache)
            self.polygon_cache.clear()

    def tags2dict(self, tags: TagList) -> dict:
        """
        Convert osmium TagList into python dict

        Arguments:
            tags {TagList} -- osmium TagList for a geo-object

        Returns:
            dict -- tags in a python dict
        """
        tag_dict: dict = {}

        for tag in tags:
            tag_dict[tag.k] = tag.v

        return tag_dict

    def node(self, node: Node):
        """
        Import OSM node into database as point

        Arguments:
            node {Node} -- osmium node object
        """

        self.count_node()

        if node.tags:
            point: PlanetOsmPoint = PlanetOsmPoint(
                osm_id=node.id,
                version=node.version,
                way=GEOSGeometry(
                    self.wkt_fab.create_point(node), srid=self.wkt_fab.epsg
                ),
                valid_since=node.timestamp,
                valid_until=self.valid_until,
                tags=self.tags2dict(tags=node.tags),
            )
            point = fill_osm_object(osm_object=point)
            self.point_cache.append(point)

    def way(self, way: Way):
        """
        Import OSM way into database as line & polygon

        Arguments:
            way {Way} -- osmium way object
        """
        self.count_way()

        if way.tags:
            tags: dict = self.tags2dict(tags=way.tags)
            clean_tags: dict = cleanup_tags(tags=tags)

            line: PlanetOsmLine = PlanetOsmLine(
                osm_id=way.id,
                version=way.version,
                way=GEOSGeometry(
                    self.wkt_fab.create_linestring(way), srid=self.wkt_fab.epsg
                ),
                valid_since=way.timestamp,
                valid_until=self.valid_until,
                tags=clean_tags,
            )
            line = fill_osm_object(osm_object=line)
            line.z_order = get_z_order(tags=clean_tags)
            self.line_cache.append(line)

            if is_road(tags=clean_tags):
                self.roads_cache.append(line.to_road())

    def area(self, area: Area):
        """
        Import osmium area into database as polygon

        Arguments:
            area {Area} -- osmium area -> ways where are close & relation as multipolygon
        """
        self.count_area()

        if area.tags:
            tags: dict = self.tags2dict(tags=area.tags)
            clean_tags: dict = cleanup_tags(tags=tags)

            poly: GEOSGeometry = GEOSGeometry(
                self.wkt_fab.create_multipolygon(area), srid=self.wkt_fab.epsg
            )

            polygon: PlanetOsmPolygon = PlanetOsmPolygon(
                osm_id=area.id,
                version=area.version,
                way=poly,
                valid_since=area.timestamp,
                valid_until=self.valid_until,
                tags=clean_tags,
            )
            polygon = fill_osm_object(osm_object=polygon)
            polygon.z_order = get_z_order(tags=clean_tags)
            polygon.way_area = poly.area
            self.polygon_cache.append(polygon)


def run_import(file_path: str, db_cache_size: int, cache2file: bool):
    """
    Start import of a osm file

    Arguments:
        file_path {str} -- path to the osm file
        db_cache_size {int} -- how much geo-object will be cache and save into at once into the database
    """
    osmhandler = OSMHandler(db_cache_size=db_cache_size)
    logger.info("import {}".format(file_path))
    osmhandler.show_import_status()

    cache_system: str = "flex_mem"
    if cache2file:
        cache_system = "dense_file_array,osmium.nodecache"

    osmhandler.apply_file(
        filename=file_path, locations=True, idx=cache_system,
    )
    osmhandler.show_import_status()
    osmhandler.save_cache()

    logger.info("Set way_area for all polygons!")
    set_polygon_way_area()

    logger.info("import done!")
