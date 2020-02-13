from datetime import datetime

from factory import DjangoModelFactory, LazyFunction


class PlanetOsmLineFactory(DjangoModelFactory):
    class Meta:
        model = "ohdm.PlanetOsmLine"
        django_get_or_create = ["osm_id"]

    osm_id = 10
    highway = "tertiary"
    name = "Test Line"
    surface = "concrete"
    way = "0102000020110F000004000000A25AE9EE9B98364101C4B88CAD505A417CE1845A94993641D40D945108515A41D87C0136D99A364198B06C68CB505A416EAD8A05869936413C5E12406E505A41"
    valid_since = datetime(2020, 1, 1)
    valid_until = datetime(2020, 12, 31)


class PlanetOsmPointFactory(DjangoModelFactory):
    class Meta:
        model = "ohdm.PlanetOsmPoint"
        django_get_or_create = ["osm_id"]

    osm_id = 20
    name = "Test Point"
    shop = "books"
    way = "0101000020110F0000C4173723919B3641888FBE379F505A41"
    valid_since = datetime(2020, 1, 1)
    valid_until = datetime(2020, 12, 31)


class PlanetOsmPolygonFactory(DjangoModelFactory):
    class Meta:
        model = "ohdm.PlanetOsmPolygon"
        django_get_or_create = ["osm_id"]

    osm_id = 30
    man_made = "bridge"
    name = "Test Brdige"
    way_area = 8835.61
    way = "0103000020110F00000100000008000000516C6048D796364166BE03001E525A41E72E2E7E5397364123241C7043515A41D3985A9AD79B3641A4C258CC4B515A413A9CAF66059B3641EB0CC26DC0525A415DF28990E9983641C0DA879975515A41836BEE24F197364166E1467CB4525A417AB1E64004983641B2F652215A515A41516C6048D796364166BE03001E525A41"
    valid_since = datetime(2020, 1, 1)
    valid_until = datetime(2020, 12, 31)


class PlanetOsmRoadsFactory(DjangoModelFactory):
    class Meta:
        model = "ohdm.PlanetOsmRoads"
        django_get_or_create = ["osm_id"]

    osm_id = 40
    highway = "secondary"
    name = "Test Road"
    oneway = "yes"
    surface = "asphalt"
    z_order = 350
    way = "0102000020110F00000500000069F0AD56F297364162C55F3B9C505A4169F0AD56F29736419D5FB9EE5C505A4180C1248745993641A5C9FBF556505A4180C124874599364177C311DEBE505A41FC726619A3983641C84B6DCA7A505A41"
    valid_since = datetime(2020, 1, 1)
    valid_until = datetime(2020, 12, 31)


class TileCacheFactory(DjangoModelFactory):
    class Meta:
        model = "ohdm.TileCache"

    created = datetime(2020, 2, 11)
    zoom = 0
    x_pixel = 0
    y_pixel = 0
    valid_since = datetime(2020, 1, 1)
    valid_until = datetime(2020, 12, 31)
    celery_task_id = "1"
    celery_task_done = False
