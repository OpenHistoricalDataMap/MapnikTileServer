import os
from datetime import date
from math import atan, pi
from math import pow as math_pow
from math import sinh
from tempfile import TemporaryDirectory
from typing import Optional

import mapnik
from config.settings.base import OSM_CARTO_STYLE_XML, env
from django.core.cache import cache
from django.db import connection
from jinja2 import Template

from ohdm_django_mapnik.ohdm.exceptions import CoordinateOutOfRange, ZoomOutOfRange

from .exceptions import RenderErrorNoDate


class TileGenerator:
    """
    based on https://wiki.openstreetmap.org/wiki/Howto_real_time_tiles_rendering_with_mapnik_and_mod_python
    """

    def __init__(
        self,
        zoom: int,
        x_pixel: float,
        y_pixel: float,
        request_date: Optional[date] = None,
        style_xml_template: str = OSM_CARTO_STYLE_XML,
        osm_cato_path: str = env("CARTO_STYLE_PATH"),
        width: int = 256,
        height: int = 256,
        use_cache: bool = False,
    ):
        """Tile generator class

        from ohdm_django_mapnik.ohdm.tile import TileGenerator
        tile_generator: TileGenerator = TileGenerator(
            zoom=0, x_pixel=0, y_pixel=0, request_date=datetime(2020, 1, 1), use_cache=False
        )
        tile_png: bytes = tile_generator.render_tile()

        Arguments:
            zoom {int} -- zoom level between 0 to 20
            x_pixel {float} -- x coordinate between 0 and 2^zoom
            y_pixel {float} -- y coordinate between 0 and 2^zoom

        Keyword Arguments:
            request_date {Optional[date]} -- request date (default: {None})
            style_xml_template {str} -- path of default style.xml (default: {OSM_CARTO_STYLE_XML})
            osm_cato_path {str} -- path of openstreetmap-carto (default: {env("CARTO_STYLE_PATH")})
            width {int} -- tile png width (default: {256})
            height {int} -- tile png height (default: {256})
            use_cache {bool} -- cache style.xml (default: {False})

        Raises:
            ZoomOutOfRange: raise when zoom level is out of range
            CoordinateOutOfRange: raise when x & y coordinate is out of range
        """

        # check if zoom level is valid
        if zoom < 0 or zoom > 19:
            raise ZoomOutOfRange(
                "Zoom level has to be between 0 and 19! zoom = {}".format(zoom)
            )

        # check if x_pixel and y_pixel is valid
        max_pixel: float = pow(2, zoom)
        if x_pixel < 0.0 or x_pixel > max_pixel or y_pixel < 0.0 or y_pixel > max_pixel:
            raise CoordinateOutOfRange(
                """
                X or Y coordinate is out of range! Coordinate has to be between 0 and 2^zoom.
                zoom = {}
                x = {}
                y = {}
                """.format(
                    zoom, x_pixel, y_pixel
                )
            )

        self.request_date: Optional[date] = request_date
        self.style_xml_template: str = style_xml_template
        self.zoom: int = zoom
        self.x_pixel: float = x_pixel
        self.y_pixel: float = y_pixel
        self.width: int = width
        self.height: int = height
        self.osm_cato_path: str = osm_cato_path
        self.use_cache = use_cache

    @staticmethod
    def from_px_to_lon(px: float, zoom: float) -> float:
        """
        Convert px coordinate into longitude

        formula:

        lon = 360 * px / 2^zoom - 180

        source: Book, OpenStreetMap, Ramm, Frederik, Topf, Jochen, page 177

        Arguments:
            px {float} -- x pixel coordinate
            zoom {float} -- zoom level

        Returns:
            float -- longitude
        """
        return 360 * (px / math_pow(2, zoom)) - 180

    @staticmethod
    def from_py_to_lat(py: float, zoom: float) -> float:
        """
        Convert py coordinate into latitude

        formula:

        lat = arctan(sinh(pi-(pi*y)/2^(zoom-1)))180/pi

        source: Book, OpenStreetMap, Ramm, Frederik, Topf, Jochen, page 177

        Arguments:
            py {float} -- y pixel coordinate
            zoom {float} -- zoom level

        Returns:
            float -- latitude
        """
        # 57.29577951308232 = 180 / pi
        return atan(sinh(pi - (pi * py) / math_pow(2, zoom - 1))) * 57.29577951308232

    def generate_date_style_xml(self) -> str:
        """
        generate style_xml for date
        :return: rendered style_xml for a date
        """

        # render current_style_xml with style_xml_template
        template: Template = Template(self.style_xml_template)
        current_style_xml: str = template.render(
            date=self.request_date, database=connection.settings_dict["NAME"]
        )

        return current_style_xml

    def get_bbox(self) -> mapnik.Box2d:
        """
        get Bounding Box from x, y, z request
        https://wiki.openstreetmap.org/wiki/Bounding_Box

        Returns:
            mapnik.Box2d -- mapnik Bounding Box
        """
        # use Mercator projection
        # https://wiki.openstreetmap.org/wiki/Mercator
        prj: mapnik.Projection = mapnik.Projection(
            "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"
        )

        # coordinates for Bounding Box
        c0: mapnik.Coord = prj.forward(
            mapnik.Coord(
                self.from_px_to_lon(px=self.x_pixel, zoom=self.zoom),
                self.from_py_to_lat(py=self.y_pixel + 1, zoom=self.zoom),
            )
        )
        c1: mapnik.Coord = prj.forward(
            mapnik.Coord(
                self.from_px_to_lon(px=self.x_pixel + 1, zoom=self.zoom),
                self.from_py_to_lat(py=self.y_pixel, zoom=self.zoom),
            )
        )

        return mapnik.Box2d(c0.x, c0.y, c1.x, c1.y)

    def render_tile(self) -> bytes:
        """
        Render tile png

        Raises:
            RenderErrorNoDate: [description]

        Returns:
            bytes -- tile png as bytes
        """

        if not self.request_date:
            raise RenderErrorNoDate("Trying to generate a tile without to set a date!")

        # move to openstreetmap-carto folder
        os.chdir(self.osm_cato_path)

        # create empty mapnik map
        mapnik_map: mapnik.Map = mapnik.Map(self.width, self.height)

        # load style_xml
        style_xml: str = ""
        if self.use_cache:
            style_key: str = "{}-style.xml".format(
                self.request_date.strftime("%Y-%m-%d")
            )
            style_xml = cache.get_or_set(style_key, self.generate_date_style_xml())
        else:
            style_xml = self.generate_date_style_xml()

        # fill map with content
        mapnik.load_map_from_string(mapnik_map, style_xml)
        mapnik_map.zoom_to_box(self.get_bbox())

        # empty mapnik image with set size
        image: mapnik.Image = mapnik.Image(self.width, self.height)

        # generate tile png
        mapnik.render(mapnik_map, image)

        # create a tmp folder for generating the tile png
        # https://docs.python.org/3/library/tempfile.html
        with TemporaryDirectory() as temp_dir:
            file_path = "{}/tile.png".format(temp_dir)
            image.save(file_path)
            return open(file_path, "rb").read()
