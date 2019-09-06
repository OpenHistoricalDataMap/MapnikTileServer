from django.contrib import admin

from .models import (
    TileCache,
    PlanetOsmLine,
    PlanetOsmPoint,
    PlanetOsmPolygon,
    PlanetOsmRoads,
)

admin.site.register(TileCache)
admin.site.register(PlanetOsmLine)
admin.site.register(PlanetOsmPoint)
admin.site.register(PlanetOsmPolygon)
admin.site.register(PlanetOsmRoads)
