from unittest import TestCase

import redis
from flask import Flask

from tile_server.app import app


class TestGenerate_default_style_xml(TestCase):
    app = Flask(__name__)
    cache = redis.Redis(host='redis', port=6379)

    def test_generate_default_style_xml(self):
        assert app.generate_default_style_xml() == ""

