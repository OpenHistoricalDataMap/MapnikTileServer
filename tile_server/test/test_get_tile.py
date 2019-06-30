from unittest import TestCase

from tile_server.app import app


class TestGet_tile(TestCase):
    def test_get_tile(self):
        assert open(app.get_tile(2013, 5, 16, 13, 4398, 2685), "rb") == open("./2685.png", "rb")
