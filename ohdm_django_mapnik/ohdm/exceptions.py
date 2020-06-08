class RenderErrorNoDate(Exception):
    """
    Called when try to render a tile without a date!
    """


class ZoomOutOfRange(Exception):
    """
    Called when try to render a tile with a zoom out of range!
    """


class CoordinateOutOfRange(Exception):
    """
    X or Y coordinate is out of range!
    """
