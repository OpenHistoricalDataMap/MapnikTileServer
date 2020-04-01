from pathlib import Path

from django.core.management.base import BaseCommand

from ohdm_django_mapnik.ohdm.import_osh import (OSMHandler, import_diff,
                                                run_import)
from ohdm_django_mapnik.ohdm.rel2pgsql import Rel2pgsql


class Command(BaseCommand):
    help = "convert osm file -> relations database -> osm2pgsql database"

    def add_arguments(self, parser):

        # drop current relations data and osm2pgsql data
        parser.add_argument(
            '--drop_current_data',
            action='store_true',
            help='Drop all current data.',
        )

        # osm object cache size for saving
        parser.add_argument(
            '--cache',
            nargs='?',
            type=int,
            help="Amount of object witch will be saved into Database at once!",
            default=10000000
        )

        # path to the planet file
        parser.add_argument('--planet', nargs='?', type=str, help="Path to the planet file.")

        # path to the diff files folder
        parser.add_argument('--diffs', nargs='?', type=str, help="Path to the day diff folder.")

        # drop current relations data and osm2pgsql data
        parser.add_argument(
            '--rel2pgsql',
            action='store_true',
            help='Convert relation data to oms2pgsql data.',
        )

    def handle(self, *args, **options):

        # drop all old data
        if options['drop_current_data']:
            OSMHandler.drop_planet_tables()

        if options['planet']:
            if not Path(options['planet']).is_file():
                print("Planet file does not exists!")
                exit(1)
            print("Start planet import!")
            run_import(file_path=options['planet'], db_cache_size=options['cache'])

        if options['diffs']:
            if not Path(options['diffs']).is_dir():
                print("Diff folder does not exists!")
                exit(1)
            print("Start diff import!")
            import_diff(diff_folder=options['diffs'], db_cache_size=options['cache'])

        # drop all old data
        if options['rel2pgsql']:
            print("Start convert rel 2 osm2pgsql!")
            rel2pgsql: Rel2pgsql = Rel2pgsql()
            rel2pgsql.run_import()
