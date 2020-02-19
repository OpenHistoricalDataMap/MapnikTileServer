import pytest
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse

from ohdm_django_mapnik.ohdm.views import generate_tile


@pytest.mark.django_db()
class TestViews:
    def test_generate_tile(self):
        year: int = 2020
        month: int = 1
        day: int = 1
        zoom: int = 0
        x_pixel: float = 0
        y_pixel: float = 0

        path: str = reverse(
            "ohdm-tile",
            kwargs={
                "year": year,
                "month": month,
                "day": day,
                "zoom": zoom,
                "x_pixel": x_pixel,
                "y_pixel": y_pixel,
            },
        )
        request: WSGIRequest = RequestFactory().get(path)
        response: HttpResponse = generate_tile(
            request=request,
            year=year,
            month=month,
            day=day,
            zoom=zoom,
            x_pixel=x_pixel,
            y_pixel=y_pixel,
        )
        assert response.status_code == 200
