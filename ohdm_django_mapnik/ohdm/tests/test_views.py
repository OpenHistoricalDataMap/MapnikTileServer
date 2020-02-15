import pytest
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse

from ohdm_django_mapnik.ohdm.views import generate_tile


@pytest.mark.django_db()
class TestViews:
    def test_generate_tile(self):
        year: int = 2019
        month: int = 10
        day: int = 10
        zoom: int = 13
        x_pixel: float = 4398
        y_pixel: float = 2685

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
