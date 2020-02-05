from datetime import date
import pytest
from mixer.backend.django import mixer
from django.core.cache import cache

from ohdm_django_mapnik.ohdm.models import (
    PlanetOsmPolygon,
    PlanetOsmLine,
    PlanetOsmPoint,
    PlanetOsmRoads,
    TileCache,
)


@pytest.mark.django_db()
class TestModels:
    def generate_planet_osm_entries(self):
        self.planet_osm_polygon_valid_since = date(year=2018, month=5, day=10)
        self.planet_osm_polygon_valid_until = date(year=2019, month=11, day=19)
        self.planet_osm_polygon: PlanetOsmPolygon = mixer.blend(
            "ohdm.PlanetOsmPolygon",
            osm_id=12,
            man_made="bridge",
            name="Test Brdige",
            way_area=8835.61,
            way="0103000020110F00000100000008000000516C6048D796364166BE03001E525A41E72E2E7E5397364123241C7043515A41D3985A9AD79B3641A4C258CC4B515A413A9CAF66059B3641EB0CC26DC0525A415DF28990E9983641C0DA879975515A41836BEE24F197364166E1467CB4525A417AB1E64004983641B2F652215A515A41516C6048D796364166BE03001E525A41",
            valid_since=self.planet_osm_polygon_valid_since,
            valid_until=self.planet_osm_polygon_valid_until,
        )

        self.planet_osm_line_valid_since = date(year=2019, month=7, day=19)
        self.planet_osm_line_valid_until = date(year=2019, month=12, day=19)
        self.planet_osm_line: PlanetOsmLine = mixer.blend(
            "ohdm.PlanetOsmLine",
            osm_id=12,
            highway="tertiary",
            name="Test Line",
            surface="concrete",
            way="0102000020110F000004000000A25AE9EE9B98364101C4B88CAD505A417CE1845A94993641D40D945108515A41D87C0136D99A364198B06C68CB505A416EAD8A05869936413C5E12406E505A41",
            valid_since=self.planet_osm_line_valid_since,
            valid_until=self.planet_osm_line_valid_until,
        )

        self.planet_osm_point_valid_since = date(year=2019, month=5, day=17)
        self.planet_osm_point_valid_until = date(year=2019, month=7, day=26)
        self.planet_osm_point: PlanetOsmPoint = mixer.blend(
            "ohdm.PlanetOsmPoint",
            osm_id=12,
            name="Test Point",
            shop="books",
            way="0101000020110F0000C4173723919B3641888FBE379F505A41",
            valid_since=self.planet_osm_point_valid_since,
            valid_until=self.planet_osm_point_valid_until,
        )

        self.planet_osm_roads_valid_since = date(year=2019, month=5, day=17)
        self.planet_osm_roads_valid_until = date(year=2019, month=7, day=26)
        self.planet_osm_road: PlanetOsmRoads = mixer.blend(
            "ohdm.PlanetOsmRoads",
            osm_id=12,
            highway="secondary",
            name="Test Road",
            oneway="yes",
            surface="asphalt",
            z_order=350,
            way="0102000020110F00000500000069F0AD56F297364162C55F3B9C505A4169F0AD56F29736419D5FB9EE5C505A4180C1248745993641A5C9FBF556505A4180C124874599364177C311DEBE505A41FC726619A3983641C84B6DCA7A505A41",
            valid_since=self.planet_osm_roads_valid_since,
            valid_until=self.planet_osm_roads_valid_until,
        )

        self.default_date: date = date(year=2019, month=8, day=10)
        self.valid_since: date = date(year=2019, month=7, day=19)
        self.valid_until: date = date(year=2019, month=7, day=26)

    def test_tile_cache_get_cache_key(self):
        tile_cache: TileCache = mixer.blend("ohdm.TileCache", pk=1)
        assert tile_cache.get_cache_key() == "t1"

    def test_tile_cache_get_tile_from_cache_or_delete(self):
        cache.set("t1", "cache-content")
        tile_cache: TileCache = mixer.blend(
            "ohdm.TileCache", pk=1, celery_task_done=True
        )
        assert tile_cache.get_tile_from_cache_or_delete() == "cache-content"

        cache.delete("t1")
        assert tile_cache.get_tile_from_cache_or_delete() is None
        assert tile_cache.pk is None

    def test_set_valid_date_iterate_objects(self):
        self.generate_planet_osm_entries()

        tile_cache: TileCache = mixer.blend("ohdm.TileCache")

        tile_cache.valid_since = None
        tile_cache.valid_until = None

        tile_cache.set_valid_date_iterate_objects(PlanetOsmPolygon.objects.all())

        assert tile_cache.valid_since == self.planet_osm_polygon_valid_since
        assert tile_cache.valid_until == self.planet_osm_polygon_valid_until

        tile_cache.set_valid_date_iterate_objects(PlanetOsmLine.objects.all())

        assert tile_cache.valid_since == self.planet_osm_line_valid_since
        assert tile_cache.valid_until == self.planet_osm_polygon_valid_until

        tile_cache.set_valid_date_iterate_objects(PlanetOsmPoint.objects.all())

        assert tile_cache.valid_since == self.valid_since
        assert tile_cache.valid_until == self.valid_until

        tile_cache.set_valid_date_iterate_objects(PlanetOsmRoads.objects.all())

        assert tile_cache.valid_since == self.valid_since
        assert tile_cache.valid_until == self.valid_until

    def test_tile_cache_set_valid_date(self):
        self.generate_planet_osm_entries()

        tile_cache: TileCache = mixer.blend(
            "ohdm.TileCache",
            zoom=14,
            x_pixel=8797,
            y_pixel=5371,
            valid_since=self.default_date,
            valid_until=self.default_date,
        )

        tile_cache.set_valid_date()
        assert tile_cache.valid_since == self.default_date
        assert tile_cache.valid_until == self.default_date

        self.generate_planet_osm_entries()
        tile_cache.set_valid_date()

        assert tile_cache.valid_since == self.valid_since
        assert tile_cache.valid_until == self.valid_until

    def test_delete(self):
        cache.set("t1", "cache-content")
        tile_cache: TileCache = mixer.blend(
            "ohdm.TileCache", pk=1, celery_task_done=True
        )
        tile_cache.delete()

        assert cache.get("t1") is None
