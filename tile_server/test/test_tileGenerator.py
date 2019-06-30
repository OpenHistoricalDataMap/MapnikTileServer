from unittest import TestCase
import datetime

from tile_server.app import app


class TestTileGenerator(TestCase):
    TestCase = app.TileGenerator(datetime.date(2013, 5, 16), app.generate_default_style_xml(), 13, 4398, 2685)

    def test_minmax_same(self):
        assert TestCase.minmax(1.0, 1.0, 1.0) == 1.0

    def test_minmax_first_middle(self):
        assert TestCase.minmax(1.0, 0.8, 2.0) == 1.0

    def test_minmax_second_middle(self):
        assert TestCase.minmax(1.0, 2.0, 3.0) == 2.0

    def test_minmax_third_middle(self):
        assert TestCase.minmax(1.34, 8.4, 5.0) == 5.0

    def test_request_date_to_string(self):
        assert TestCase.request_date_to_string() == "2013-05-16"

    def test_render_tile(self):
        assert TestCase.rende_tile() == open("./2685.png", "rb")

    def test_from_px_to_ll(self):
        assert TestCase.from_px_to_ll([TestCase.x_pixel, TestCase.y_pixel], 3) == (593.0859375, -89.29849168340932)
