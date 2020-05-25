import pytest

from ohdm_django_mapnik.ohdm.postgis_utily import set_indexes


@pytest.mark.django_db()
def test_set_indexes():
    set_indexes()
