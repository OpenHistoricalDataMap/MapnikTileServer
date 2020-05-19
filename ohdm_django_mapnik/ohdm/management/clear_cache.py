from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Clear-Up Cache"

    def handle(self, *args, **options):
        print("comming soon...")
