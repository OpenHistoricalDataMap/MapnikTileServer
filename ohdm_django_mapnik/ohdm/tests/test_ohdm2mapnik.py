import pytest

from ohdm_django_mapnik.ohdm.ohdm2mapnik import Ohdm2Mapnik


@pytest.mark.django_db()
def test_ohdm2mapnik():
    ohdm2mapnik: Ohdm2Mapnik = Ohdm2Mapnik()
    ohdm2mapnik.run()
