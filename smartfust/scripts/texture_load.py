from pygame import image, transform

def load_texture(texture_path, size=None, smoothscale=None, smoothscale_factor=None):
    texture = image.load(texture_path)
    if not size and not smoothscale:
        return texture
    if smoothscale_factor:
        new_width = texture.get_width() * smoothscale_factor
        new_height = texture.get_height() * smoothscale_factor
        size = (new_width, new_height)
    return transform.smoothscale(texture, size)
