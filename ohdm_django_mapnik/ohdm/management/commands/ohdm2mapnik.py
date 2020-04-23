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

    def handle(self, *args, **options):
        # drop all old data
        if options["clear_mapnik_db"]:
            clear_mapnik_tables()

        ohdm2mapnik: Ohdm2Mapnik = Ohdm2Mapnik(chunk_size=options["cache"], continue_old_import=options["continue"])
        ohdm2mapnik.run()
