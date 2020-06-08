from ohdm_django_mapnik.ohdm.tags2mapnik import (
    cleanup_tags,
    get_z_order,
    is_linestring,
    is_polygon,
    is_road,
    roads_info,
)


def test_is_polygon():
    # check polygon_keys
    if is_polygon(tags={"craft": "value"}) is not True:
        raise AssertionError
    if is_polygon(tags={"craft:key": "value"}) is not False:
        raise AssertionError

    # check polygon_values
    if is_polygon(tags={"aerialway": "station"}) is not True:
        raise AssertionError
    if is_polygon(tags={"aerialway": "value"}) is not False:
        raise AssertionError


def test_is_linestring():
    # check linestring_values
    if is_linestring(tags={"golf": "cartpath"}) is not True:
        raise AssertionError
    if is_linestring(tags={"golf": "value"}) is not False:
        raise AssertionError


def test_cleanup_tags():
    test_tags: dict = {"note:key": "note", "stay": "stay", "note": "delete"}
    clean_tags: dict = cleanup_tags(tags=test_tags)

    if clean_tags["key"] != "note":
        raise AssertionError
    if clean_tags["stay"] != "stay":
        raise AssertionError
    if clean_tags.get("note") != None:
        raise AssertionError


def test_get_z_order():
    if (
        get_z_order(tags={"highway": "motorway"})
        != roads_info["highway"]["motorway"]["z"]
    ):
        raise AssertionError
    if get_z_order(tags={"highway": "value"}) != 0:
        raise AssertionError
    if (
        get_z_order(
            tags={"highway": "motorway", "railway": "narrow_gauge", "note": "value"}
        )
        != roads_info["highway"]["motorway"]["z"]
        + roads_info["railway"]["narrow_gauge"]["z"]
    ):
        raise AssertionError


def test_is_road():
    if is_road(tags={"highway": "motorway"}) is not True:
        raise AssertionError
    if is_road(tags={"aeroway": "runway", "highway": "motorway"}) is not True:
        raise AssertionError
    if is_road(tags={"aeroway": "runway"}) is not False:
        raise AssertionError
    if is_road(tags={"highway": "value"}) is not False:
        raise AssertionError
