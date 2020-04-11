from typing import Any, List

# based on https://github.com/gravitystorm/openstreetmap-carto/blob/master/openstreetmap-carto.lua

# Objects with any of the following keys will be treated as polygon
polygon_keys: List[str] = [
    "abandoned:aeroway",
    "abandoned:amenity",
    "abandoned:building",
    "abandoned:landuse",
    "abandoned:power",
    "aeroway",
    "allotments",
    "amenity",
    "area:highway",
    "craft",
    "building",
    "building:part",
    "club",
    "golf",
    "emergency",
    "harbour",
    "healthcare",
    "historic",
    "landuse",
    "leisure",
    "man_made",
    "military",
    "natural",
    "office",
    "place",
    "power",
    "public_transport",
    "shop",
    "tourism",
    "water",
    "waterway",
    "wetland",
]

# Objects with any of the following key/value combinations will be treated as linestring
linestring_values = {
    "golf": ["cartpath", "hole", "path"],
    "emergency": ["designated", "destination", "no", "official", "yes"],
    "historic": ["citywalls"],
    "leisure": ["track", "slipway"],
    "man_made": ["breakwater", "cutline", "embankment", "groyne", "pipeline"],
    "natural": ["cliff", "earth_bank", "tree_row", "ridge", "arete"],
    "power": ["cable", "line", "minor_line"],
    "tourism": ["yes"],
    "waterway": [
        "canal",
        "derelict_canal",
        "ditch",
        "drain",
        "river",
        "stream",
        "tidal_channel",
        "wadi",
        "weir",
    ],
}

# Objects with any of the following key/value combinations will be treated as polygon
polygon_values: dict = {
    "aerialway": ["station"],
    "boundary": ["aboriginal_lands", "national_park", "protected_area"],
    "highway": ["services", "rest_area"],
    "junction": ["yes"],
    "railway": ["station"],
}

# The following keys will be deleted
delete_tags: List[str] = [
    "note",
    "source",
    "source_ref",
    "attribution",
    "comment",
    "fixme",
    # Tags generally dropped by editors, not otherwise covered
    "created_by",
    "odbl",
    # Lots of import tags
    # EUROSHA (Various countries)
    "project:eurosha_2012",
    # UrbIS (Brussels, BE)
    "ref:UrbIS",
    # NHN (CA)
    "accuracy:meters",
    "waterway:type",
    # StatsCan (CA)
    "statscan:rbuid",
    # RUIAN (CZ)
    "ref:ruian:addr",
    "ref:ruian",
    "building:ruian:type",
    # DIBAVOD (CZ)
    "dibavod:id",
    # UIR-ADR (CZ)
    "uir_adr:ADRESA_KOD",
    # GST (DK)
    "gst:feat_id",
    # osak (DK)
    "osak:identifier",
    # Maa-amet (EE)
    "maaamet:ETAK",
    # FANTOIR (FR)
    "ref:FR:FANTOIR",
    # OPPDATERIN (NO)
    "OPPDATERIN",
    # Various imports (PL)
    "addr:city:simc",
    "addr:street:sym_ul",
    "building:usage:pl",
    "building:use:pl",
    # TERYT (PL)
    "teryt:simc",
    # RABA (SK)
    "raba:id",
    # LINZ (NZ)
    "linz2osm:objectid",
    # DCGIS (Washington DC, US)
    "dcgis:gis_id",
    # Building Identification Number (New York, US)
    "nycdoitt:bin",
    # Chicago Building Inport (US)
    "chicago:building_id",
    # Louisville, Kentucky/Building Outlines Import (US)
    "lojic:bgnum",
    # MassGIS (Massachusetts, US)
    "massgis:way_id",
    # misc
    "import",
    "import_uuid",
    "OBJTYPE",
    "SK53_bulk:load",
]
delete_prefixes: List[str] = [
    "note:",
    "source:",
    # Corine (CLC) (Europe)
    "CLC:",
    # Geobase (CA)
    "geobase:",
    # CanVec (CA)
    "canvec:",
    # Geobase (CA)
    "geobase:",
    # kms (DK)
    "kms:",
    # ngbe (ES)
    # See also note:es and source:file above
    "ngbe:",
    # Friuli Venezia Giulia (IT)
    "it:fvg:",
    # KSJ2 (JA)
    # See also note:ja and source_ref above
    "KSJ2:",
    # Yahoo/ALPS (JA)
    "yh:",
    # LINZ (NZ)
    "LINZ2OSM:",
    "LINZ:",
    # WroclawGIS (PL)
    "WroclawGIS:",
    # Naptan (UK)
    "naptan:",
    # TIGER (US)
    "tiger:",
    # GNIS (US)
    "gnis:",
    # National Hydrography Dataset (US)
    "NHD:",
    "nhd:",
    # mvdgis (Montevideo, UY)
    "mvdgis:",
]

# Big table for z_order and roads status for certain tags. z=0 is turned into
# nil by the z_order function
roads_info: dict = {
    "highway": {
        "motorway": {"z": 380, "roads": True},
        "trunk": {"z": 370, "roads": True},
        "primary": {"z": 360, "roads": True},
        "secondary": {"z": 350, "roads": True},
        "tertiary": {"z": 340, "roads": False},
        "residential": {"z": 330, "roads": False},
        "unclassified": {"z": 330, "roads": False},
        "road": {"z": 330, "roads": False},
        "living_street": {"z": 320, "roads": False},
        "pedestrian": {"z": 310, "roads": False},
        "raceway": {"z": 300, "roads": False},
        "motorway_link": {"z": 240, "roads": True},
        "trunk_link": {"z": 230, "roads": True},
        "primary_link": {"z": 220, "roads": True},
        "secondary_link": {"z": 210, "roads": True},
        "tertiary_link": {"z": 200, "roads": False},
        "service": {"z": 150, "roads": False},
        "track": {"z": 110, "roads": False},
        "path": {"z": 100, "roads": False},
        "footway": {"z": 100, "roads": False},
        "bridleway": {"z": 100, "roads": False},
        "cycleway": {"z": 100, "roads": False},
        "steps": {"z": 90, "roads": False},
        "platform": {"z": 90, "roads": False},
    },
    "railway": {
        "rail": {"z": 440, "roads": True},
        "subway": {"z": 420, "roads": True},
        "narrow_gauge": {"z": 420, "roads": True},
        "light_rail": {"z": 420, "roads": True},
        "funicular": {"z": 420, "roads": True},
        "preserved": {"z": 420, "roads": False},
        "monorail": {"z": 420, "roads": False},
        "miniature": {"z": 420, "roads": False},
        "turntable": {"z": 420, "roads": False},
        "tram": {"z": 410, "roads": False},
        "disused": {"z": 400, "roads": False},
        "construction": {"z": 400, "roads": False},
        "platform": {"z": 90, "roads": False},
    },
    "aeroway": {
        "runway": {"z": 60, "roads": False},
        "taxiway": {"z": 50, "roads": False},
    },
    "boundary": {"administrative": {"z": 0, "roads": True}},
}


def is_polygon(tags: dict) -> bool:
    """
    check if object is a polygon based on the tags
    
    Arguments:
        tags {dict} -- Tags dict
    
    Returns:
        bool -- True -> polygon, False -> no polygon
    """
    key: str
    value: str
    for key, value in tags.items():
        # check polygon_keys
        if key in polygon_keys:
            return True

        # check polygon_values
        if key in polygon_values:
            if value in polygon_values[key]:
                return True

    return False


def is_linestring(tags: dict) -> bool:
    """
    check if object is a linestring based on the tags
    
    Arguments:
        tags {dict} -- Tags dict
    
    Returns:
        bool -- True -> linestring, False -> no linestring
    """
    key: str
    value: str
    for key, value in tags.items():
        # check linestring_values
        if key in linestring_values:
            if value in linestring_values[key]:
                return True

    return False


def cleanup_tags(tags: dict) -> dict:
    """
    remove not import tags and remove some prefixes
    
    Arguments:
        tags {dict} -- Tags dict
    
    Returns:
        dict -- cleaned up tags
    """
    clean_tags: dict = {}
    key: str
    value: str
    for key, value in tags.items():
        for delete_prefix in delete_prefixes:
            if key.startswith(delete_prefix):
                key = key[len(delete_prefix) :]
                break
        if key not in delete_tags:
            clean_tags[key] = value

    return clean_tags


def get_z_order(tags: dict) -> int:
    """
    compute the z_order based on the tags
    
    Arguments:
        tags {dict} -- Tags dict
    
    Returns:
        int -- z_order value
    """
    z_order: int = 0
    key: str
    value: str
    for key, value in tags.items():
        # check roads_info
        try:
            z_order += roads_info[key][value]["z"]
        except KeyError:
            pass

    return z_order


def is_road(tags: dict) -> bool:
    """
    check if given tags are a road
    
    Arguments:
        tags {dict} -- Tags dict
    
    Returns:
        bool -- is road
    """
    key: str
    value: str
    for key, value in tags.items():
        # check roads_info
        try:
            if roads_info[key][value]["roads"]:
                return True
        except KeyError:
            pass
    return False


def fill_osm_object(osm_object: Any) -> Any:
    """
    fill osm object like PlanetOsmLine, PlanetOsmPoint, PlanetOsmPolygon
    
    Arguments:
        osm_object {Any} -- PlanetOsmLine, PlanetOsmPoint or PlanetOsmPolygon
    
    Returns:
        Any -- filtered osm object
    """
    filtered_tags: dict = {}

    key: str
    value: str
    for key, value in osm_object.tags.items():
        try:
            if isinstance(value, osm_object.osm_fields[key]):
                setattr(
                    osm_object, key, value,
                )
            else:
                filtered_tags[key] = value
        except KeyError:
            filtered_tags[key] = value

    osm_object.tags = filtered_tags
    return osm_object
