from django.core.management.base import BaseCommand
from ohdm_django_mapnik.ohdm.prerender import prerender


class Command(BaseCommand):
    help = "Prerender Tiles"

    def add_arguments(self, parser):

        parser.add_argument(
            "--zoom-level",
            nargs="?",
            type=int,
            help="Set the zoom level, how deeply should be prerendert",
            default=10,
        )

    def handle(self, *args, **options):
        prerender(zoom_level=options["zoom-level"])
