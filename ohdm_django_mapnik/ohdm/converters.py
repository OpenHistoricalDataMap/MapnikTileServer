class FloatConverter:
    """
    convert a float string to a float value
    """

    regex = "[\d\.\d]+"

    def to_python(self, value):
        return float(value)

    def to_url(self, value):
        return "{}".format(value)
