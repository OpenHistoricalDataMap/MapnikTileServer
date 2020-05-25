from datetime import date

import pytest

from ohdm_django_mapnik.ohdm.models import (
    PlanetOsmLine,
    PlanetOsmPoint,
    PlanetOsmPolygon,
)
from ohdm_django_mapnik.ohdm.prerender import prerender


@pytest.mark.django_db()
def test_prerender():
    PlanetOsmPoint.objects.create(
        valid_since=date(2020, 1, 3), valid_until=date(2020, 1, 1),
    )

    PlanetOsmLine.objects.create(
        valid_since=date(2020, 1, 2), valid_until=date(2020, 1, 2),
    )

    PlanetOsmPolygon.objects.create(
        valid_since=date(2020, 1, 1), valid_until=date(2020, 1, 3),
    )

    prerender(zoom_level=0)
