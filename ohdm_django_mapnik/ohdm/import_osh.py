from datetime import datetime, timedelta
from subprocess import call
from time import sleep
from typing import Any, Dict, List, Optional, Tuple

import shapely.wkb as wkblib
from django.contrib.gis.gdal import CoordTransform, SpatialReference
from django.contrib.gis.geos.collections import MultiPolygon
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.contrib.gis.geos.point import Point
from django.core.cache import cache
from osmium import SimpleHandler
from osmium._osmium import InvalidLocationError
from osmium.geom import WKTFactory
from osmium.osm._osm import (
    Area,
    Changeset,
    Location,
    Node,
    NodeRef,
    Relation,
    RelationMember,
    RelationMemberList,
    Tag,
    TagList,
    Way,
    WayNodeList,
)
from osmium.replication.server import ReplicationServer

from .models import (
    PlanetOsmLine,
    PlanetOsmNodes,
    PlanetOsmPoint,
    PlanetOsmPolygon,
    PlanetOsmRels,
    PlanetOsmRoads,
    PlanetOsmWays,
    TileCache,
)


class OSMHandler(SimpleHandler):
    def __init__(self):
        SimpleHandler.__init__(self)

        # A global factory that creates WKB from a osmium geometry
        self.wkt_fab: WKTFactory = WKTFactory()

        self.node_cache: List[PlanetOsmNodes] = []
        self.way_cache: List[PlanetOsmWays] = []
        self.rel_cache: List[PlanetOsmRels] = []

        self.node_counter: int = 0
        self.way_counter: int = 0
        self.rel_counter: int = 0

        print("starting import ...")

    def show_import_status(self):
        if (self.node_counter + self.way_counter + self.rel_counter) % 10000 == 0:
            self.delete_last_terminal_line()
            print(
                "Nodes: {} | Ways: {} | Rel: {}".format(
                    self.node_counter, self.way_counter, self.rel_counter
                )
            )

    def delete_last_terminal_line(self):
        print(
            "\033[A                                   \033[A"
        )  # delete last terminal output

    def check_cache_save(self):
        if (self.node_counter + self.way_counter + self.rel_counter) % 10000000 == 0:
            self.save_cache()

    def count_node(self):
        self.node_counter += 1
        self.check_cache_save()

        self.show_import_status()

    def count_way(self):
        self.way_counter += 1
        self.check_cache_save()

        self.show_import_status()

    def count_rel(self):
        self.rel_counter += 1
        self.check_cache_save()

        self.show_import_status()

    def drop_planet_tables(self):
        """
        Drop all data from mapnik tables and tile cache
        """
        PlanetOsmLine.objects.all().delete()
        PlanetOsmPoint.objects.all().delete()
        PlanetOsmPolygon.objects.all().delete()
        PlanetOsmRoads.objects.all().delete()
        TileCache.objects.all().delete()

        PlanetOsmNodes.objects.all().delete()
        PlanetOsmRels.objects.all().delete()
        PlanetOsmWays.objects.all().delete()

    def save_cache(self):
        print("saving cache ...")
        PlanetOsmNodes.objects.bulk_create(self.node_cache)
        PlanetOsmWays.objects.bulk_create(self.way_cache)
        PlanetOsmRels.objects.bulk_create(self.rel_cache)
        self.delete_last_terminal_line()

        self.node_cache.clear()
        self.way_cache.clear()
        self.rel_cache.clear()

    def tags2dict(self, tags: TagList) -> dict:
        tag_dict: dict = {}

        for tag in tags:
            tag_dict[tag.k] = tag.v

        return tag_dict

    def node(self, node: Node):
        node_db: PlanetOsmNodes = PlanetOsmNodes(
            osm_id=node.id, version=node.version,
        )

        if node.deleted:
            node_db.delete = node.timestamp
        else:
            node_db.timestamp = node.timestamp
            node_db.point = Point(node.location.lat, node.location.lon)
            node_db.tags = self.tags2dict(tags=node.tags)

        self.node_cache.append(node_db)

        self.count_node()

    def way(self, way: Way):
        way_db: PlanetOsmWays = PlanetOsmWays(
            osm_id=way.id, version=way.version,
        )

        if way.deleted:
            way_db.delete = way.timestamp
        else:
            way_db.timestamp = way.timestamp
            way_db.tags = self.tags2dict(tags=way.tags)
            way_db.way = GEOSGeometry(
                self.wkt_fab.create_linestring(way), srid=self.wkt_fab.epsg
            )

        self.way_cache.append(way_db)

        self.count_way()

    def relation(self, rel: Relation):
        # if rel.tags.get("type") == "multipolygon" or rel.tags.get("type") == "border":

        inner_members: List[str] = []
        outer_members: List[str] = []
        for member in rel.members:
            if member.type == "w":
                if member.role == "inner":
                    inner_members.append(member.ref)
                if member.role == "outer":
                    outer_members.append(member.ref)

        rel_db: PlanetOsmRels = PlanetOsmRels(
            osm_id=rel.id, version=rel.version,
        )

        if rel.deleted:
            rel_db.delete = rel.timestamp
        else:
            rel_db.timestamp = rel.timestamp
            rel_db.tags = self.tags2dict(tags=rel.tags)
            rel_db.role = rel.role
            rel_db.inner_members = inner_members
            rel_db.outer_members = outer_members

        self.rel_cache.append(rel_db)

        self.count_rel()


def run_import():
    osmhandler = OSMHandler()
    osmhandler.drop_planet_tables()

    osmhandler.show_import_status()
    osmhandler.apply_file(
        filename="/app/planet-120912.osm.bz2", locations=True, idx="flex_mem",
    )

    osmhandler.show_import_status()
    osmhandler.save_cache()
