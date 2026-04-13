from random import randint
import colorsys

def random_rgb():
    return (randint(0, 255), randint(0, 255), randint(0, 255))

def titlelize(word: str, marge: int=2) -> str:
    """ Stylise un titre """
    return f"{'-' * (len(word) + 2 * marge + 2)}\n|{' ' * marge}{word}{' ' * marge}|\n{'-' * (len(word) + 2 * marge + 2)}"



def blend_colors(foreground, background, alpha):
    r1, g1, b1 = foreground
    r2, g2, b2 = background

    r = int(r1 * alpha + r2 * (1 - alpha))
    g = int(g1 * alpha + g2 * (1 - alpha))
    b = int(b1 * alpha + b2 * (1 - alpha))

    return (r, g, b)



def are_identical_colors(c1, c2, delta_h=0.01):
    r1, g1, b1 = [x/255 for x in c1]
    r2, g2, b2 = [x/255 for x in c2]

    h1, s1, v1 = colorsys.rgb_to_hsv(r1, g1, b1)
    h2, s2, v2 = colorsys.rgb_to_hsv(r2, g2, b2)

    return abs(h1 - h2) < delta_h
