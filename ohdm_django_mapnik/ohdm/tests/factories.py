from datetime import datetime

from factory import DjangoModelFactory

from ohdm_django_mapnik.ohdm.tasks import auto_done_task


class PlanetOsmLineFactory(DjangoModelFactory):
    class Meta:
        model = "ohdm.PlanetOsmLine"
        django_get_or_create = ["osm_id"]

    # url http://127.0.0.1:8000/2020/1/1/15/17595/10743/reload-style-xml/tile.png

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

    # url http://127.0.0.1:8000/2020/1/1/15/17594/10743/reload-style-xml/tile.png

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

    # url http://127.0.0.1:8000/2020/1/1/15/17594/10742/reload-style-xml/tile.png

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

    # url http://127.0.0.1:800/2123/03/16/18/140759/85950/reload-style-xml/tile.png

    osm_id = 40
    highway = "primary"
    name = "Test Road"
    oneway = "yes"
    surface = "asphalt"
    z_order = 350
    way = "010200000002000000AE1FAC30E49836416ED53F8574505A4141D7BE0805993641E9A9C49368505A41"
    valid_since = datetime(2020, 1, 1)
    valid_until = datetime(2020, 12, 31)


class FinishTileCacheFactory(DjangoModelFactory):
    class Meta:
        model = "ohdm.TileCache"

    created = datetime(2020, 2, 11)
    zoom = 0
    x_pixel = 0
    y_pixel = 0
    valid_since = datetime(2020, 1, 1)
    valid_until = datetime(2020, 12, 31)
    celery_task_id = auto_done_task.delay(seconds=0).id
    celery_task_done = True


class RunningTileCacheFactory(FinishTileCacheFactory):

    celery_task_id = auto_done_task.delay(seconds=10).id
    celery_task_done = False
