import math
import os

import redis
from flask import Flask, make_response
from datetime import date
import mapnik
import subprocess
from jinja2 import Template
from envparse import env

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)


def generate_default_style_xml() -> str:
    """
    Generate with carto and project.mml the default style.xml with jinja2 vars
    :return: jinja2 Template for custom date style.xml
    """
    # generate mapnik xml and return it to a string
    response = subprocess.run("carto /opt/openstreetmap-carto/style.mml 1>&2",
                              cwd="/opt/openstreetmap-carto",
                              shell=True, stderr=subprocess.PIPE)
    return response.stderr.decode("utf-8")


class TileGenerator:
    """
    based on https://wiki.openstreetmap.org/wiki/Howto_real_time_tiles_rendering_with_mapnik_and_mod_python
    """

    def __init__(self, request_date: date, style_xml_template: str, zoom: int, x_pixel: float, y_pixel: float,
                 levels: int = 20, width: int = 256, height: int = 256):
        self.request_date: date = request_date
        self.style_xml_template: str = style_xml_template
        self.zoom: int = zoom
        self.x_pixel: float = x_pixel
        self.y_pixel: float = y_pixel
        self.width: int = width
        self.height: int = height

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
        return self.request_date.strftime('%Y-%m-%d')

    def generate_date_style_xml(self) -> str:
        """
        generate style_xml for date
        :return: rendered style_xml for a date
        """
        # set style filename
        style_file: str = "{}-project.mml".format(self.request_date_to_string())

        if env.bool("CACHE", default=False):
            # try if exists to get cache style_xml
            try:
                current_style_xml = cache.get(style_file)
                if current_style_xml:
                    return current_style_xml
            except (redis.exceptions.ConnectionError, redis.exceptions.DataError) as exc:
                print(exc)

        # render current_style_xml with style_xml_template
        template: Template = Template(self.style_xml_template)
        current_style_xml: str = template.render(date=self.request_date)

        if env.bool("CACHE", default=False):
            # upload style_xml file to redis cache
            cache.set(style_file, current_style_xml, ex=env.int("CAHCE_EXPIRE_TIME", default=3600))

        import codecs
        file = codecs.open("/app/{}-style.xml".format(self.request_date_to_string()), "w", "utf-8")
        file.write(current_style_xml)
        file.close()



        return current_style_xml

    def render_tile(self) -> bytes:
        """
        generate tile or load it from redis cache
        :return:  tile as png image in bytes format
        """
        tile_name: str = '/tmp/{}-{}-{}-{}.png'.format(
            self.request_date_to_string(),
            self.zoom,
            self.x_pixel,
            self.y_pixel
        )

        if env.bool("CACHE", default=False):
            # try if exists to get cache style_xml
            try:
                tile_content = cache.get(tile_name)
                if tile_content:
                    return tile_content
            except (redis.exceptions.ConnectionError, redis.exceptions.DataError) as exc:
                print(exc)

        os.chdir(os.environ['STYLE_PATH'])
        map: mapnik.Map = mapnik.Map(self.width, self.height)
        mapnik.load_map_from_string(map, self.generate_date_style_xml())

        prj: mapnik.Projection = mapnik.Projection(
            "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over")

        p0 = self.from_px_to_ll((self.width * self.x_pixel, self.height * (self.y_pixel + 1)), self.zoom)
        p1 = self.from_px_to_ll((self.width * (self.x_pixel + 1), self.height * self.y_pixel), self.zoom)
        c0 = prj.forward(mapnik.Coord(p0[0], p0[1]))
        c1 = prj.forward(mapnik.Coord(p1[0], p1[1]))

        bbox: mapnik.Envelope = mapnik.Envelope(c0.x, c0.y, c1.x, c1.y)

        map.zoom_to_box(bbox)
        image: mapnik.Image = mapnik.Image(self.width, self.height)
        mapnik.render(map, image)

        # todo generate tile without save it to hdd
        mapnik.render_to_file(map, tile_name)
        tile_content: bytes = open(tile_name, 'rb').read()
        os.remove(tile_name)

        if env.bool("CACHE", default=False):
            # upload style_xml file to redis cache
            cache.set(tile_name, tile_content, ex=env.int("CAHCE_EXPIRE_TIME", default=3600))

        return tile_content


# default jinja2 template sytle_xml
style_xml: str = generate_default_style_xml()


@app.route('/tile/<year>/<month>/<day>/<zoom>/<x_pixel>/<y_pixel>.png', methods=['GET'])
def get_tile(year: int, month: int, day: int, zoom: int, x_pixel: float, y_pixel: float):
    """
    Generate tile or load it from redis cache
    :param year: year in YYYY
    :param month: month in MM
    :param day: Day in DD
    :param zoom: Zoom
    :param x_pixel: leaflet x px
    :param y_pixel: leaflet y px
    :return: tile as png img
    """

    # generate tile
    tile_gen: TileGenerator = TileGenerator(
        request_date=date(year=int(year), month=int(month), day=int(day)),
        style_xml_template=style_xml,
        zoom=int(zoom),
        x_pixel=float(x_pixel),
        y_pixel=float(y_pixel),
    )

    # create http response
    response = make_response(tile_gen.render_tile())
    response.headers.set('Content-Type', 'image/png')
    return response


# Entrypoint of flask microservice
if __name__ == "__main__":
    app.run(host=os.environ['HOSTNAME'], debug=env.bool("DEBUG", default=False))
