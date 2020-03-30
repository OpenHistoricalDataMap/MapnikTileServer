from django.core.management.base import BaseCommand

from ohdm_django_mapnik.ohdm.import_osh import run_import
from ohdm_django_mapnik.ohdm.rel2pgsql import Rel2pgsql


class Command(BaseCommand):
    help = "generate a default style.xml"

    def handle(self, *args, **options):
        run_import()
        # rel2pgsql: Rel2pgsql = Rel2pgsql()
        # rel2pgsql.run_import()
