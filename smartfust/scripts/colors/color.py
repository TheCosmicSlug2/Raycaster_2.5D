def clamp_byte(byte):
    return min(max(0, byte), 255)

def clamp_rgb(rgb):
    r, g, b = rgb
    return clamp_byte(r), clamp_byte(g), clamp_byte(b)

def clamp_rgb_add(rgb, value):
    r, g, b = rgb
    r += value
    g += value
    b += value
    return clamp_rgb((r, g, b))

class Color:
    def __init__(self, rgba):
        if len(rgba) == 3:
            self.r, self.g, self.b = rgba
            self.a = 255
        else:
            self.r, self.g, self.b, self.a = rgba

    @property
    def rgba(self):
        return (self.r, self.g, self.b, self.a)

    @property
    def rgb(self):
        return (self.r, self.g, self.b)

    def add(self, value):
        self.r, self.g, self.b = clamp_rgb_add(self.rgb, value)

    def invert(self):
        self.r = 255 - self.r
        self.g = 255 - self.g
        self.b = 255 - self.b
