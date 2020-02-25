from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from ohdm_django_mapnik.ohdm.models import (
    OhdmContent,
    OhdmExternalSystems,
    OhdmExternalUsers,
    OhdmGeoobject,
    OhdmGeoobjectContent,
    OhdmGeoobjectGeometry,
    OhdmGeoobjectUrl,
    OhdmImportUpdates,
    OhdmLayer,
    OhdmLines,
    OhdmPoints,
    OhdmPolygons,
    OhdmSubsequentGeomUser,
    OhdmTopology,
    OhdmUrl,
)

from .models import (
    OhdmClassification,
    PlanetOsmLine,
    PlanetOsmPoint,
    PlanetOsmPolygon,
    PlanetOsmRoads,
    TileCache,
)


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

# ohdm
admin.site.register(OhdmClassification)
admin.site.register(OhdmContent)
admin.site.register(OhdmExternalSystems)
admin.site.register(OhdmExternalUsers)
admin.site.register(OhdmGeoobject)
admin.site.register(OhdmGeoobjectContent)
admin.site.register(OhdmGeoobjectGeometry)
admin.site.register(OhdmGeoobjectUrl)
admin.site.register(OhdmImportUpdates)
admin.site.register(OhdmLayer)
admin.site.register(OhdmLines)
admin.site.register(OhdmPoints)
admin.site.register(OhdmPolygons)
admin.site.register(OhdmSubsequentGeomUser)
admin.site.register(OhdmTopology)
admin.site.register(OhdmUrl)
