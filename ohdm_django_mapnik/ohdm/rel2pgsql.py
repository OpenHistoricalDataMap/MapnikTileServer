import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

from django.contrib.gis.geos.collections import MultiPolygon
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.contrib.gis.geos.polygon import Polygon
from django.utils import timezone
from shapely.geometry import Polygon as ShapelyPolygon

from .models import (PlanetOsmLine, PlanetOsmNodes, PlanetOsmPoint,
                     PlanetOsmPolygon, PlanetOsmRels, PlanetOsmRoads,
                     PlanetOsmWays)
from .postgis_utily import make_polygon_valid, set_polygon_way_area
from .tags2mapnik import fill_osm_object, get_z_order, is_linestring, is_road

logger = logging.getLogger(__name__)

class NodeVersion:
    def __init__(self, timestamp: datetime):
        self.nodes: List[PlanetOsmNodes] = []
        self.osm_id: Optional[int] = None
        self.timestamp = timestamp

    def add_node(self, node: PlanetOsmNodes) -> Optional[List[PlanetOsmPoint]]:
        if not self.osm_id:
            self.osm_id = node.osm_id

        if self.osm_id == node.osm_id:
            self.nodes.append(node)
        else:
            return self.convert2pgsql()
        return None

    def convert2pgsql(self) -> List[PlanetOsmPoint]:
        previous_timestamp: date = self.timestamp
        node: PlanetOsmNodes
        points: List[PlanetOsmPoint] = []
        for node in self.nodes:
            if not node.visible and node.timestamp:
                previous_timestamp = node.timestamp
                continue
            if node.tags:
                point: PlanetOsmPoint = PlanetOsmPoint(
                    osm_id=node.osm_id,
                    version=node.version,
                    way=node.point,
                    valid_since=node.timestamp,
                    valid_until=previous_timestamp,
                    tags=node.tags,
                )
                point = fill_osm_object(osm_object=point)
                points.append(point)
            if node.timestamp:
                previous_timestamp = node.timestamp

        self.nodes.clear()
        self.osm_id = None
        return points


class WayVersion:
    def __init__(self, timestamp: datetime):
        self.ways: List[PlanetOsmWays] = []
        self.osm_id: Optional[int] = None
        self.timestamp = timestamp

    def add_way(
        self, way: PlanetOsmWays
    ) -> Optional[
        Tuple[List[PlanetOsmLine], List[PlanetOsmRoads], List[PlanetOsmPolygon]]
    ]:
        if not self.osm_id:
            self.osm_id = way.osm_id

        if self.osm_id == way.osm_id:
            self.ways.append(way)
        else:
            return self.convert2pgsql()
        return None

    def convert2pgsql(
        self,
    ) -> Tuple[List[PlanetOsmLine], List[PlanetOsmRoads], List[PlanetOsmPolygon]]:
        previous_timestamp: date = self.timestamp
        way: PlanetOsmWays
        lines: List[PlanetOsmLine] = []
        roads: List[PlanetOsmRoads] = []
        polygons: List[PlanetOsmPolygon] = []
        for way in self.ways:
            if not way.visible and way.timestamp:
                previous_timestamp = way.timestamp
                continue
            if way.tags and way.way:
                if way.way.closed:
                    # create polygon with shapely & repair if needed
                    poly: ShapelyPolygon = ShapelyPolygon(way.way.coords)
                    if not poly.is_valid:
                        # fix polygon
                        poly = poly.buffer(distance=0)

                    polygon: PlanetOsmPolygon = PlanetOsmPolygon(
                        osm_id=way.osm_id,
                        version=way.version,
                        way=GEOSGeometry(poly.wkt),
                        valid_since=way.timestamp,
                        valid_until=previous_timestamp,
                        tags=way.tags,
                    )
                    polygon = fill_osm_object(osm_object=polygon)
                    polygon.z_order = get_z_order(tags=way.tags)
                    polygons.append(polygon)

                # if not way.way.closed or way.way.closed and is_linestring(tags=way.tags):
                line: PlanetOsmLine = PlanetOsmLine(
                    osm_id=way.osm_id,
                    version=way.version,
                    way=way.way,
                    valid_since=way.timestamp,
                    valid_until=previous_timestamp,
                    tags=way.tags,
                )
                line = fill_osm_object(osm_object=line)
                line.z_order = get_z_order(tags=way.tags)
                lines.append(line)

                if is_road(tags=way.tags):
                    roads.append(line.to_road())

            if way.timestamp:
                previous_timestamp = way.timestamp

        self.ways.clear()
        self.osm_id = None
        return (lines, roads, polygons)


class RelationVersion:
    def __init__(self, timestamp: datetime):
        self.rels: List[PlanetOsmRels] = []
        self.osm_id: Optional[int] = None
        self.timestamp = timestamp

    def add_rel(self, rel: PlanetOsmRels) -> Optional[List[PlanetOsmPolygon]]:
        if not self.osm_id:
            self.osm_id = rel.osm_id

        if self.osm_id == rel.osm_id:
            self.rels.append(rel)
        else:
            return self.convert2pgsql()
        return None

    def convert2pgsql(self) -> List[PlanetOsmPolygon]:
        # https://wiki.openstreetmap.org/wiki/Relation:multipolygon/Algorithm

        previous_timestamp: date = self.timestamp
        rel: PlanetOsmRels
        multipolygons: List[PlanetOsmPolygon] = []
        for rel in self.rels:
            if (
                not rel.visible
                or not rel.outer_members
                or not rel.inner_members
                or not rel.tags
            ):
                if rel.timestamp:
                    previous_timestamp = rel.timestamp
                continue

            if rel.rel_type != "multipolygon" and rel.rel_type != "boundary":
                continue

            ways: Dict[int, PlanetOsmWays] = {}
            way: PlanetOsmWays
            for way in PlanetOsmWays.objects.filter(
                osm_id__in=rel.outer_members, visible=True
            ).order_by("osm_id", "-version"):
                if not way.way or not way.way.closed:
                    # todo combine not closed ways
                    continue
                if way.osm_id in ways:
                    if way.timestamp <= ways[way.osm_id].timestamp:
                        ways[way.osm_id] = way
                else:
                    ways[way.osm_id] = way

            for way in PlanetOsmWays.objects.filter(
                osm_id__in=rel.inner_members, visible=True
            ).order_by("osm_id", "-version"):
                if not way.way or not way.way.closed:
                    # todo combine not closed ways
                    continue
                if way.osm_id in ways:
                    if way.timestamp <= ways[way.osm_id].timestamp:
                        ways[way.osm_id] = way
                else:
                    ways[way.osm_id] = way

            polygons: List[Polygon] = []

            for osm_id in rel.outer_members:
                if osm_id in ways:
                    polygons.append(Polygon(ways[osm_id].way.coords))
            for osm_id in rel.inner_members:
                if osm_id in ways:
                    polygons.append(Polygon(ways[osm_id].way.coords))

            multipolygon: MultiPolygon = MultiPolygon(polygons)

            polygon: PlanetOsmPolygon = PlanetOsmPolygon(
                osm_id=rel.osm_id,
                version=rel.version,
                way=GEOSGeometry(multipolygon.wkt),
                valid_since=rel.timestamp,
                valid_until=previous_timestamp,
                tags=rel.tags,
            )
            polygon = fill_osm_object(osm_object=polygon)
            multipolygons.append(polygon)
            previous_timestamp = rel.timestamp

        self.rels.clear()
        self.osm_id = None
        return multipolygons


class Rel2pgsql:
    def __init__(self, chunk_size: int):
        self.chunk_size = chunk_size

        self.timestamp: datetime = self.set_last_timestamp()

        self.point_cache: List[PlanetOsmPoint] = []
        self.line_cache: List[PlanetOsmLine] = []
        self.road_cache: List[PlanetOsmRoads] = []
        self.polygon_cache: List[PlanetOsmPolygon] = []

        self.point_counter: int = 0
        self.line_counter: int = 0
        self.polygon_counter: int = 0

        # estimate total amount ob mapnik objects
        self.total_rows: int = 0

        # process start time
        self.start_time: float = 0

    def set_last_timestamp(self) -> datetime:
        nodes: List[PlanetOsmNodes] = PlanetOsmNodes.objects.order_by("-timestamp")[:1]
        ways: List[PlanetOsmWays] = PlanetOsmWays.objects.order_by("-timestamp")[:1]
        rels: List[PlanetOsmRels] = PlanetOsmRels.objects.order_by("-timestamp")[:1]

        timestamp: datetime = timezone.now()

        if len(nodes) != 0:
            timestamp: datetime = nodes[0].timestamp
        if len(ways) != 0 and ways[0].timestamp > timestamp:
            timestamp = ways[0].timestamp
        if len(rels) != 0 and rels[0].timestamp > timestamp:
            timestamp = rels[0].timestamp

        return timestamp

    def show_status(self):
        if (self.point_counter + self.line_counter + self.point_counter) % 10000 == 0:
            logger.info(
                "Points: {} | Lines/Polygon: {} | Multipolygon: {}".format(
                    self.point_counter, self.line_counter, self.polygon_counter
                )
            )

    def check_cache_save(self):
        if (
            self.point_counter + self.line_counter + self.point_counter
        ) % self.chunk_size == 0:
            self.save_cache()

    def save_cache(self):
        logger.info("saving cache ...")
        if self.point_cache:
            PlanetOsmPoint.objects.bulk_create(self.point_cache)
            self.point_cache.clear()
        if self.line_cache:
            PlanetOsmLine.objects.bulk_create(self.line_cache)
            self.line_cache.clear()
        if self.road_cache:
            PlanetOsmRoads.objects.bulk_create(self.road_cache)
            self.road_cache.clear()
        if self.polygon_cache:
            PlanetOsmPolygon.objects.bulk_create(self.polygon_cache)
            self.polygon_cache.clear()

    def run_import(self):
        logger.info()
        self.make_points()
        self.make_lines()
        # todo fix multipolygon
        # self.make_multipolygon()
        self.save_cache()
        self.update_polygons()
        logger.info("import done")

    def make_points(self):
        # https://docs.djangoproject.com/en/3.0/ref/models/querysets/#django.db.models.query.QuerySet.iterator
        node: PlanetOsmNodes
        node_version: NodeVersion = NodeVersion(timestamp=self.timestamp)
        for node in PlanetOsmNodes.objects.order_by("osm_id", "-version").iterator(
            chunk_size=self.chunk_size
        ):
            point_cache: Optional[List[PlanetOsmPoint]] = node_version.add_node(
                node=node
            )
            if point_cache:
                self.point_cache += point_cache
            self.point_counter += 1
            self.show_status()
            self.check_cache_save()

    def make_lines(self):
        # https://docs.djangoproject.com/en/3.0/ref/models/querysets/#django.db.models.query.QuerySet.iterator
        way: PlanetOsmWays
        way_version: WayVersion = WayVersion(timestamp=self.timestamp)
        for way in PlanetOsmWays.objects.order_by("osm_id", "-version").iterator(
            chunk_size=self.chunk_size
        ):
            line_cache: Optional[
                Tuple[List[PlanetOsmLine], List[PlanetOsmRoads], List[PlanetOsmPolygon]]
            ] = way_version.add_way(way=way)
            if line_cache:
                self.line_cache += line_cache[0]
                self.road_cache += line_cache[1]
                self.polygon_cache += line_cache[2]
            self.line_counter += 1
            self.show_status()
            self.check_cache_save()

    def make_multipolygon(self):
        rel: PlanetOsmRels
        rel_version: RelationVersion = RelationVersion(timestamp=self.timestamp)
        for rel in PlanetOsmRels.objects.order_by("osm_id", "-version").iterator(
            chunk_size=self.chunk_size
        ):
            rel_cache: Optional[List[PlanetOsmPolygon]] = rel_version.add_rel(rel=rel)
            if rel_cache:
                self.polygon_cache += rel_cache
            self.polygon_counter += 1
            self.show_status()
            self.check_cache_save()

    def update_polygons(self):
        logger.info("Make invalid polygons valid!")
        make_polygon_valid()
        logger.info("Set way_area for all polygons!")
        set_polygon_way_area()
