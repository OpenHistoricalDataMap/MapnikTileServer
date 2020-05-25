from typing import List

from django.core.management.base import BaseCommand
from ohdm_django_mapnik.ohdm.clear_db import clear_mapnik_tables
from ohdm_django_mapnik.ohdm.ohdm2mapnik import Ohdm2Mapnik


class Command(BaseCommand):
    help = "convert database from ohdm 2 mapnik"

    def add_arguments(self, parser):

        # drop current mapnik (osm2pgsql) data & tile cache
        parser.add_argument(
            "--clear_mapnik_db",
            action="store_true",
            help="Clear mapnik (osm2pgsql) data & tile cache",
        )

        # osm object cache size for saving
        parser.add_argument(
            "--cache",
            nargs="?",
            type=int,
            help="Amount of object witch will be handel at once!",
            default=100000,
        )

        parser.add_argument(
            "--convert_points",
            action="store_true",
            help="Points convert will be enabled, if set, only enabled geometries will be converted. By default, all geometries will be converted.",
        )

        parser.add_argument(
            "--convert_lines",
            action="store_true",
            help="Lines convert will be enabled, if set, only enabled geometries will be converted. By default, all geometries will be converted.",
        )

        parser.add_argument(
            "--convert_polygons",
            action="store_true",
            help="Polygons convert will be enabled, if set, only enabled geometries will be converted. By default, all geometries will be converted.",
        )

        parser.add_argument(
            "--convert_threads",
            nargs="?",
            type=int,
            help="How many rows should be converted at once.",
            default=1,
        )

        parser.add_argument(
            "--sql_threads",
            nargs="?",
            type=int,
            help="How many threats should be use, to insert entries into the database.",
            default=1,
        )

        parser.add_argument(
            "--not-fill-ohdm-tables",
            action="store_true",
            help="Do not fill the ohdm cache table.",
        )

    def handle(self, *args, **options):
        # drop all old data
        if options["clear_mapnik_db"]:
            clear_mapnik_tables()

        geometries: List[str] = []

        # set geometries
        if options["convert_points"]:
            geometries.append("point")
        if options["convert_lines"]:
            geometries.append("line")
        if options["convert_polygons"]:
            geometries.append("polygon")

        if len(geometries) == 0:
            geometries = ["point", "line", "polygon"]

        ohdm2mapnik: Ohdm2Mapnik = Ohdm2Mapnik(
            chunk_size=options["cache"],
            geometries=geometries,
            sql_threads=options["sql_threads"],
            convert_threads=options["convert_threads"],
        )

        if not options["not-fill-ohdm-tables"]:
            ohdm2mapnik.fill_ohdm_geoobject_tables()

        ohdm2mapnik.run()
