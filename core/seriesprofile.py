class SeriesProfile:
    def __init__(self, **kwarg):
        self.lineWidth = None
        self.point = None
        self.line = True
        self.color = (1, 1, 1, 1)
        self.label = ""

        if "line" in kwarg: self.lineWidth = kwarg["line"]
        if "point" in kwarg: self.point = kwarg["point"]
        if "color" in kwarg:
            color = int(kwarg["color"], 16)
            # Set alpha to opaque if not specified
            if (color >> 24) & 0xff == 0: color = color | 0xff000000
            self.color = (((color >> 16) & 0xff) / 256.0,
                            ((color >>  8) & 0xff) / 256.0,
                            ((color      ) & 0xff) / 256.0,
                            ((color >> 24) & 0xff) / 256.0)