from django.core.management.base import BaseCommand
from ohdm_django_mapnik.ohdm.postgis_utily import set_indexes


class Command(BaseCommand):
    help = "Set indexes"

    def handle(self, *args, **options):
        print("Indexes will be set!")
        set_indexes()
