from django.urls import reverse, resolve


class TestUrls:
    def test_default_tile_url(self):
        path: str = reverse(
            "ohdm-tile",
            kwargs={
                "year": 2019,
                "month": 2,
                "day": 10,
                "zoom": 13,
                "x_pixel": 4398,
                "y_pixel": 2685,
            },
        )
        assert resolve(path).view_name == "ohdm-tile"
