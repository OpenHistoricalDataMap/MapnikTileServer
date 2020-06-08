from time import sleep

from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Clear cache"

    def handle(self, *args, **options):
        print("All cache files will be deleted, this can be undo!")
        print("You have 15 seconds to stop this process with pressing ctrl + c")

        for seconds in range(15, 0, -5):
            print("{}s remaining ...".format(seconds))
            sleep(5)

        print("Cache will be delete!")
        cache.clear()
        print("Cache is now clean")
