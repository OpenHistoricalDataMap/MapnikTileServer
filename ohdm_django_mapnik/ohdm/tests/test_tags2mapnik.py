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
    assert is_polygon(tags={"craft": "value"}) is True
    assert is_polygon(tags={"craft:key": "value"}) is False

    # check polygon_values
    assert is_polygon(tags={"aerialway": "station"}) is True
    assert is_polygon(tags={"aerialway": "value"}) is False


def test_is_linestring():
    # check linestring_values
    assert is_linestring(tags={"golf": "cartpath"}) is True
    assert is_linestring(tags={"golf": "value"}) is False


def test_cleanup_tags():
    test_tags: dict = {"note:key": "note", "stay": "stay", "note": "delete"}
    clean_tags: dict = cleanup_tags(tags=test_tags)

    assert clean_tags["key"] == "note"
    assert clean_tags["stay"] == "stay"
    assert clean_tags.get("note") == None


def test_get_z_order():
    assert (
        get_z_order(tags={"highway": "motorway"})
        == roads_info["highway"]["motorway"]["z"]
    )
    assert get_z_order(tags={"highway": "value"}) == 0
    assert (
        get_z_order(
            tags={"highway": "motorway", "railway": "narrow_gauge", "note": "value"}
        )
        == roads_info["highway"]["motorway"]["z"]
        + roads_info["railway"]["narrow_gauge"]["z"]
    )


def test_is_road():
    assert is_road(tags={"highway": "motorway"}) is True
    assert is_road(tags={"aeroway": "runway", "highway": "motorway"}) is True
    assert is_road(tags={"aeroway": "runway"}) is False
    assert is_road(tags={"highway": "value"}) is False
