from pathlib import Path

from django.core.management.base import BaseCommand
from ohdm_django_mapnik.ohdm.clear_db import clear_mapnik_tables
from ohdm_django_mapnik.ohdm.import_osm import run_import


class Command(BaseCommand):
    help = "convert osm file -> osm2pgsql database"

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
            help="Amount of object which will be handle at once!",
            default=100000,
        )

        # set cache system for osmium, default is flex_mem
        parser.add_argument(
            "--cache2file",
            action="store_true",
            help="Cache osmium extraction into a file instead of memory",
        )

        # path to the planet file
        parser.add_argument(
            "--planet", nargs="?", type=str, help="Path to the planet file."
        )

    def handle(self, *args, **options):

        # drop all old data
        if options["clear_mapnik_db"]:
            clear_mapnik_tables()

        if options["planet"]:
            if not Path(options["planet"]).is_file():
                print("Planet file does not exists!")
                exit(1)
            print("Start planet import!")
            run_import(
                file_path=options["planet"],
                db_cache_size=options["cache"],
                cache2file=options["cache2file"],
            )
        else:
            print("No Planet was selected, please add --planet path")
