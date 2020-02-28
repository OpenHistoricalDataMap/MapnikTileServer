from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import (PlanetOsmLine, PlanetOsmPoint, PlanetOsmPolygon,
                     PlanetOsmRoads, TileCache)


class TileCacheAdmin(admin.ModelAdmin):
    list_display = (
        "celery_task_id",
        "created",
        "celery_task_done",
        "zoom",
        "x_pixel",
        "y_pixel",
        "valid_since",
        "valid_until",
    )
    list_filter = ["celery_task_done", "zoom", "valid_since", "valid_until"]
    search_fields = [
        "celery_task_id",
        "created",
        "valid_since",
        "valid_until",
        "zoom",
        "x_pixel",
        "y_pixel",
    ]


class PlanetOsmAdmin(OSMGeoAdmin):
    list_display = (
        "osm_id",
        "geoobject",
        "name",
        "boundary",
        "natural",
        "tags",
        "valid_since",
        "valid_until",
    )
    list_filter = ["natural", "valid_since", "valid_until"]
    search_fields = ["osm_id", "name"]


admin.site.register(TileCache, TileCacheAdmin)
admin.site.register(PlanetOsmLine, PlanetOsmAdmin)
admin.site.register(PlanetOsmPoint, PlanetOsmAdmin)
admin.site.register(PlanetOsmPolygon, PlanetOsmAdmin)
admin.site.register(PlanetOsmRoads, PlanetOsmAdmin)
