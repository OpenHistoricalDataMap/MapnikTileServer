from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import PlanetOsmLine, PlanetOsmPoint, PlanetOsmPolygon, PlanetOsmRoads


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


admin.site.register(PlanetOsmLine, PlanetOsmAdmin)
admin.site.register(PlanetOsmPoint, PlanetOsmAdmin)
admin.site.register(PlanetOsmPolygon, PlanetOsmAdmin)
admin.site.register(PlanetOsmRoads, PlanetOsmAdmin)
