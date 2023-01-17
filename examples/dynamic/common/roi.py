class ROI:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __repr__(self):
        return str(self)

    def __str__(self):
        txt = f"ROI(x={self.x}, y={self.y}, w={self.w}, h={self.h})"
        return txt
