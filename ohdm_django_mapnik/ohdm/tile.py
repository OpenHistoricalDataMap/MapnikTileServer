import math
import os

from datetime import date
import mapnik
from jinja2 import Template
from django.core.cache import cache


class TileGenerator:
    """
    based on https://wiki.openstreetmap.org/wiki/Howto_real_time_tiles_rendering_with_mapnik_and_mod_python
    """

    def __init__(
        self,
        zoom: int,
        x_pixel: float,
        y_pixel: float,
        request_date: date = None,
        style_xml_template: str = None,
        osm_cato_path: str = None,
        levels: int = 20,
        width: int = 256,
        height: int = 256,
        use_cache: bool = False,
    ):
        self.request_date: date = request_date
        self.style_xml_template: str = style_xml_template
        self.zoom: int = zoom
        self.x_pixel: float = x_pixel
        self.y_pixel: float = y_pixel
        self.width: int = width
        self.height: int = height
        self.osm_cato_path: str = osm_cato_path
        self.use_cache = use_cache

        self.Bc = []
        self.Cc = []
        self.zc = []
        self.Ac = []
        c = 256
        for d in range(0, levels):
            e = c / 2
            self.Bc.append(c / 360.0)
            self.Cc.append(c / (2 * math.pi))
            self.zc.append((e, e))
            self.Ac.append(c)
            c *= 2

    @staticmethod
    def minmax(a: float, b: float, c: float) -> float:
        a = max(a, b)
        a = min(a, c)
        return a

    def from_px_to_ll(self, px, zoom) -> (float, float):
        e = self.zc[zoom]
        f = (px[0] - e[0]) / self.Bc[zoom]
        g = (px[1] - e[1]) / -self.Cc[zoom]
        h = math.degrees(2 * math.atan(math.exp(g)) - 0.5 * math.pi)
        return f, h

    def request_date_to_string(self) -> str:
        """
        convert request_date to string
        :return: string %Y-%m-%d
        """
        return self.request_date.strftime("%Y-%m-%d")

    def generate_date_style_xml(self) -> str:
        """
        generate style_xml for date
        :return: rendered style_xml for a date
        """

        # render current_style_xml with style_xml_template
        template: Template = Template(self.style_xml_template)
        current_style_xml: str = template.render(date=self.request_date)

        return current_style_xml

    def get_bbox(self) -> mapnik.Envelope:
        prj: mapnik.Projection = mapnik.Projection(
            "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"
        )

        p0 = self.from_px_to_ll(
            (self.width * self.x_pixel, self.height * (self.y_pixel + 1)), self.zoom
        )
        p1 = self.from_px_to_ll(
            (self.width * (self.x_pixel + 1), self.height * self.y_pixel), self.zoom
        )
        c0 = prj.forward(mapnik.Coord(p0[0], p0[1]))
        c1 = prj.forward(mapnik.Coord(p1[0], p1[1]))

        return mapnik.Envelope(c0.x, c0.y, c1.x, c1.y)

    def render_tile(self) -> bytes:
        """
        generate tile or load it from redis cache
        :return:  tile as png image in bytes format
        """
        tile_name: str = "/tmp/{}-{}-{}-{}.png".format(
            self.request_date_to_string(), self.zoom, self.x_pixel, self.y_pixel
        )

        os.chdir(self.osm_cato_path)
        map: mapnik.Map = mapnik.Map(self.width, self.height)

        if self.use_cache:
            style_key: str = "{}-style.xml".format(self.request_date_to_string())
            style_xml: str = cache.get_or_set(style_key, self.generate_date_style_xml())
        else:
            style_xml: str = self.generate_date_style_xml()

        mapnik.load_map_from_string(map, style_xml)

        map.zoom_to_box(self.get_bbox())
        image: mapnik.Image = mapnik.Image(self.width, self.height)
        mapnik.render(map, image)

        # todo generate tile without save it to hdd
        mapnik.render_to_file(map, tile_name)
        tile_content: bytes = open(tile_name, "rb").read()
        os.remove(tile_name)

        return tile_content
