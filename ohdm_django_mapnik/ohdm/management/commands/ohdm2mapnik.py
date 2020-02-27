from django.core.management.base import BaseCommand

from ohdm_django_mapnik.ohdm.ohdm2mapnik import Ohdm2Mapnik


class Command(BaseCommand):
    help = "convert database from ohdm 2 mapnik"

    def handle(self, *args, **options):
        ohdm2mapnik: Ohdm2Mapnik = Ohdm2Mapnik()
        ohdm2mapnik.run()
