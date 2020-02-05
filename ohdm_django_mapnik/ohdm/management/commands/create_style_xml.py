from django.core.management.base import BaseCommand

from config.settings.base import env
from ohdm_django_mapnik.ohdm.utily import create_style_xml


class Command(BaseCommand):
    help = "generate a default style.xml"

    def handle(self, *args, **options):
        create_style_xml(carto_sytle_path=env("CARTO_STYLE_PATH"))
