from typing import List

from django.contrib.gis.gdal import CoordTransform, SpatialReference
from django.contrib.gis.geos import LinearRing
# from django.contrib.gis.geos.collections import MultiPolygon
from django.contrib.gis.geos.geometry import GEOSGeometry
from osmium.geom import WKTFactory
# from django.contrib.gis.geos.polygon import Polygon
from shapely.geometry import Polygon
from shapely.geometry.multipolygon import MultiPolygon
# from django.contrib.gis.geos.linestring import LinearRing, LineString
from shapely.geometry.polygon import LinearRing, LineString

from osgeo.ogr import Geometry, wkbMultiPolygon, wkbPolygon

from .models import (PlanetOsmLine, PlanetOsmNodes, PlanetOsmPoint,
                     PlanetOsmPolygon, PlanetOsmRels, PlanetOsmRoads,
                     PlanetOsmWays, TileCache)


class Rel2pgsql():

    def __init__(self):
        # A global factory that creates WKB from a osmium geometry
        self.wkt_fab: WKTFactory = WKTFactory()

        # https://docs.djangoproject.com/en/3.0/ref/contrib/gis/gdal/#coordtransform
        self.ct: CoordTransform = CoordTransform(
            SpatialReference(self.wkt_fab.epsg), SpatialReference(3857)
        )

    def run_import(self):
        self.make_multipolygon()

    def make_multipolygon(self):
        rels: List[PlanetOsmRels] = PlanetOsmRels.objects.all()

        for rel in rels:
            # multipolygon: Geometry = Geometry(wkbMultiPolygon)
            polygons: List[Polygon] = []

            for outer_member in rel.outer_members:

                # load last way bevor new rel version

                ways: List[PlanetOsmWays] = PlanetOsmWays.objects.filter(
                    osm_id=outer_member,
                    timestamp__lte=rel.timestamp).order_by('version')[:1]

                if ways[0].timestamp > rel.timestamp:
                    print("rel: {} way: {}".format(rel.timestamp, ways[0].timestamp))
                else:
                    print(len(ways))

                # way: PlanetOsmWays = PlanetOsmWays.objects.get(osm_id=outer_member)
            #     try:
            #         polygons.append(Polygon(ways[0].way))
            #     except ValueError:
            #         continue
                
            # for inner_member in rel.inner_members:

            #     way: PlanetOsmWays = PlanetOsmWays.objects.get(osm_id=outer_member)
            #     try:
            #         polygons.append(Polygon(way.way))
            #     except ValueError:
            #         continue 

            # mulipolygon: MultiPolygon = MultiPolygon(polygons)
