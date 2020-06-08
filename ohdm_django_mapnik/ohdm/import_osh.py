import logging
from typing import List

from django.contrib.gis.geos.geometry import GEOSGeometry
from osmium import SimpleHandler
from osmium._osmium import InvalidLocationError
from osmium.geom import WKTFactory
from osmium.osm._osm import Node, Relation, TagList, Way

from .models import PlanetOsmNodes, PlanetOsmRels, PlanetOsmWays
from .tags2mapnik import cleanup_tags

logger = logging.getLogger(__name__)


class OSMHandler(SimpleHandler):
    def __init__(self, db_cache_size: int):
        SimpleHandler.__init__(self)

        # A global factory that creates WKB from a osmium geometry
        self.wkt_fab: WKTFactory = WKTFactory()

        self.node_cache: List[PlanetOsmNodes] = []
        self.way_cache: List[PlanetOsmWays] = []
        self.rel_cache: List[PlanetOsmRels] = []

        self.node_counter: int = 0
        self.way_counter: int = 0
        self.rel_counter: int = 0

        self.db_cache_size: int = db_cache_size

        logger.info("starting import ...")

    def show_import_status(self):
        """
        Show import status for every 10000 objects
        """
        if (self.node_counter + self.way_counter + self.rel_counter) % 10000 == 0:
            logger.info(
                "Nodes: {} | Ways: {} | Rel: {}".format(
                    self.node_counter, self.way_counter, self.rel_counter
                )
            )

    def check_cache_save(self):
        """
        Check if chuck_size is succeed & save cached geo-objects
        """
        if (
            self.node_counter + self.way_counter + self.rel_counter
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

    def count_rel(self):
        """
        Count Relation, check for save cache & show import status
        """
        self.rel_counter += 1
        self.check_cache_save()

        self.show_import_status()

    def save_cache(self):
        """
        Save cached geo-objects into database & clear cache
        """
        logger.info("saving cache ...")
        if self.node_cache:
            PlanetOsmNodes.objects.bulk_create(self.node_cache)
            self.node_cache.clear()
        if self.way_cache:
            PlanetOsmWays.objects.bulk_create(self.way_cache)
            self.way_cache.clear()
        if self.rel_cache:
            PlanetOsmRels.objects.bulk_create(self.rel_cache)
            self.rel_cache.clear()

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

        return cleanup_tags(tags=tag_dict)

    def node(self, node: Node):
        """
        Import OSM node into database as node
        
        Arguments:
            node {Node} -- osmium node object
        """
        node_db: PlanetOsmNodes = PlanetOsmNodes(
            osm_id=node.id,
            version=node.version,
            visible=node.visible,
            timestamp=node.timestamp,
        )

        if node.location.valid():
            node_db.point = GEOSGeometry(
                self.wkt_fab.create_point(node), srid=self.wkt_fab.epsg
            )
            node_db.tags = self.tags2dict(tags=node.tags)

        self.node_cache.append(node_db)

        self.count_node()

    def way(self, way: Way):
        """
        Import OSM way into database as way
        
        Arguments:
            way {Way} -- osmium way object
        """
        modes: List[int] = []
        for node in way.nodes:
            modes.append(node.ref)

        way_db: PlanetOsmWays = PlanetOsmWays(
            osm_id=way.id,
            version=way.version,
            visible=way.visible,
            timestamp=way.timestamp,
        )

        try:
            way_db.way = GEOSGeometry(
                self.wkt_fab.create_linestring(way), srid=self.wkt_fab.epsg
            )
            way_db.tags = (self.tags2dict(tags=way.tags),)
        except (RuntimeError, InvalidLocationError):
            pass

        self.way_cache.append(way_db)

        self.count_way()

    def relation(self, rel: Relation):
        """
        Import OSM relation into database as relation
        
        Arguments:
            rel {Relation} -- osmium relation object
        """

        rel_db: PlanetOsmRels = PlanetOsmRels(
            osm_id=rel.id,
            version=rel.version,
            visible=rel.visible,
            timestamp=rel.timestamp,
            rel_type=rel.tags.get("type"),
        )

        if rel.visible:
            rel_db.tags = self.tags2dict(tags=rel.tags)
            for member in rel.members:
                if not member.type == "w":
                    continue
                if member.role == "inner":
                    rel_db.inner_members.append(member.ref)
                if member.role == "outer":
                    rel_db.outer_members.append(member.ref)

        self.rel_cache.append(rel_db)

        self.count_rel()


def run_import(file_path: str, db_cache_size: int, cache2file: bool):
    """
    start import of a osh (OpenStreetMap history file) into relation tables
    
    Arguments:
        file_path {str} -- path to a osh file
        db_cache_size {int} -- chunk size for import
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
    logger.info("import done!")
