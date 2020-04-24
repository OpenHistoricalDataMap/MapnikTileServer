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

        # continue old ohdm2mapnik command
        parser.add_argument(
            "--continue",
            action="store_true",
            help="Continue a previous ohdm2mapnik command, useful when the command was interrupted",
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
            "--convert-points",
            action="store_true",
            help="Points convert will be enabled, if set, only enabled geometries will be converted. By default, all geometries will be converted.",
        )

        parser.add_argument(
            "--convert-lines",
            action="store_true",
            help="Lines convert will be enabled, if set, only enabled geometries will be converted. By default, all geometries will be converted.",
        )

        parser.add_argument(
            "--convert-polygons",
            action="store_true",
            help="Polygons convert will be enabled, if set, only enabled geometries will be converted. By default, all geometries will be converted.",
        )

    def handle(self, *args, **options):
        # drop all old data
        if options["clear_mapnik_db"]:
            clear_mapnik_tables()

        geometries: List[str] = []

        # set geometries
        if options["points"]:
            geometries.append("points")
        if options["lines"]:
            geometries.append("lines")
        if options["polygons"]:
            geometries.append("polygons")

        if len(geometries) == 0:
            geometries = ["points", "lines", "polygons"]

        ohdm2mapnik: Ohdm2Mapnik = Ohdm2Mapnik(chunk_size=options["cache"], continue_old_import=options["continue"], geometries=geometries)
        ohdm2mapnik.run()
