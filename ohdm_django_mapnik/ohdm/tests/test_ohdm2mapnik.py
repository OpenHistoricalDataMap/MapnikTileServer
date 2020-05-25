import pytest
from django.db import connection

from ohdm_django_mapnik.ohdm.models import (
    GeoobjectGeometry,
    OhdmGeoobjectLine,
    OhdmGeoobjectPoint,
    OhdmGeoobjectPolygon,
    PlanetOsmLine,
    PlanetOsmPoint,
    PlanetOsmPolygon,
)


@pytest.mark.django_db()
class TestOhdm2mapnik:
    def test_ohdm2mapnik(self, ohdm2mapnik):
        """test complete import
        """
        ohdm2mapnik.fill_ohdm_geoobject_tables()
        ohdm2mapnik.run()

        assert (
            PlanetOsmPoint.objects.all().count()
            == OhdmGeoobjectPoint.objects.all().count()
        )
        assert (
            PlanetOsmLine.objects.all().count()
            == OhdmGeoobjectLine.objects.all().count()
        )
        assert (
            PlanetOsmPolygon.objects.all().count()
            >= OhdmGeoobjectPolygon.objects.all().count() / 100 * 98
        )

    def test_fill_ohdm_geoobject_tables(self, ohdm2mapnik):
        """test if the function fill_ohdm_geoobject_tables fill the ohdm objects tables correctly
        """
        ohdm2mapnik.fill_ohdm_geoobject_tables()
        ohdm_objects: int = OhdmGeoobjectPoint.objects.all().count() + OhdmGeoobjectLine.objects.all().count() + OhdmGeoobjectPolygon.objects.all().count()
        assert ohdm_objects >= GeoobjectGeometry.objects.all().count() / 100 * 97
