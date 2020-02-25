import pytest

from ohdm_django_mapnik.ohdm.ohdm2mapnik import ohdm2mapnik


@pytest.mark.django_db()
def test_ohdm2mapnik():
    ohdm2mapnik()
