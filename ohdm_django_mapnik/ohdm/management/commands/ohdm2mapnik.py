from django.core.management.base import BaseCommand

from config.settings.base import env
from ohdm_django_mapnik.ohdm.ohdm2mapnik import ohdm2mapnik


class Command(BaseCommand):
    help = "convert database from ohdm 2 mapnik"

    def handle(self, *args, **options):
        ohdm2mapnik()
