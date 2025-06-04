from pygame import image, transform

def load_texture(texture_path, size=None, smoothscale=None):
    texture = image.load(texture_path)
    if not size and not smoothscale:
        return texture
    if smoothscale:
        new_width = texture.get_width() * smoothscale
        new_height = texture.get_height() * smoothscale
        size = (new_width, new_height)
    return transform.smoothscale(texture, size)
