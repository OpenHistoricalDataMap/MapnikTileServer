from pathlib import Path

from django.core.management.base import BaseCommand

from ohdm_django_mapnik.ohdm.clear_db import clear_mapnik_tables, clear_rel_tables
from ohdm_django_mapnik.ohdm.import_osh import run_import
from ohdm_django_mapnik.ohdm.rel2pgsql import Rel2pgsql


class Command(BaseCommand):
    help = "convert osh file -> relations database -> osm2pgsql database"

    def add_arguments(self, parser):

        # drop current relations data and osm2pgsql data
        parser.add_argument(
            "--clear_rel_db", action="store_true", help="Clear relation data",
        )

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

        # drop current relations data and osm2pgsql data
        parser.add_argument(
            "--rel2pgsql",
            action="store_true",
            help="Convert relation data to oms2pgsql data.",
        )

    def handle(self, *args, **options):

        # drop all old data
        if options["clear_rel_db"]:
            clear_rel_tables()
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

        if options["rel2pgsql"]:
            print("Start convert rel 2 osm2pgsql!")
            rel2pgsql: Rel2pgsql = Rel2pgsql(chunk_size=options["cache"])
            rel2pgsql.run_import()
