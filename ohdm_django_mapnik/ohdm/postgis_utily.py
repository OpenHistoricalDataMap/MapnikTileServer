from config.settings.base import env
from django.db import connection


def make_polygon_valid():
    """
    Make all invalid polygons in table planet_osm_polygon valid
    with a Postgres SQL statement
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE public.planet_osm_polygon
            SET way = ST_MakeValid(way)
            WHERE ST_IsValid(way) is false;
        """
        )


def set_polygon_way_area():
    """
    Update for all polygons in planet_osm_polygon the way_area column
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE public.planet_osm_polygon
            SET way_area = ST_Area(way);
        """
        )


def set_indexes(osm_cato_path: str = env("CARTO_STYLE_PATH")):
    """
    Set SQL indexes, to speedup rendering
    """
    with open("{}/indexes.sql".format(osm_cato_path)) as index:
        index_sql: str = index.read()
        with connection.cursor() as cursor:
            cursor.execute(index_sql)
