from tkinter import W
from pygame import cursors, time, Surface, draw, Rect, mouse, \
    SYSTEM_CURSOR_ARROW, SYSTEM_CURSOR_IBEAM, SYSTEM_CURSOR_HAND, display
import pygame as pg
from smartfust.scripts.texture_load import load_texture
from smartfust.scripts.wgs.widgets import *
from smartfust.scripts.colors.color import clamp_rgb_add

class Renderer:
    def __init__(self, screen_size):
        self.screen_size = screen_size
        self.FPS = 30
        self.clock = time.Clock()
        self.bg = None

        self.cursors = {
            "arrow": cursors.Cursor(SYSTEM_CURSOR_ARROW),
            "ibeam": cursors.Cursor(SYSTEM_CURSOR_IBEAM),
            "hand": cursors.Cursor(SYSTEM_CURSOR_HAND)
        }
        self.cache = pg.Surface(self.screen_size, pg.SRCALPHA)

    def set_bg(self, _type, dims, colors, array, image_path, shadow) -> None:
        self.bg = Surface(self.screen_size, pg.SRCALPHA)
        if _type == "none":
            return
        if _type == "rgb":
            self.bg.fill(colors)
        if _type == "chessboard":
            # Create array
            array = [[(column + row) % 2 for column in range(dims[0])] for row in range(dims[1])]
        if _type == "image":
            self.bg = load_texture(image_path, self.screen_size, True)

        if _type in ("custom", "chessboard"):
            dims = (len(array[0]), len(array))
            cell_width = self.screen_size[0] // dims[0]
            cell_height = self.screen_size[1] // dims[1]
            shadow_sign = shadow["sign"]
            shadow_mult = shadow["mult"]
            dx = shadow_sign[0]
            dy = shadow_sign[1]
            dic = dict(enumerate(colors))
            for row_idx, row in enumerate(array):
                for column_idx, column in enumerate(row):
                    color = dic[column]

                    from_center_x = abs(dims[1] // 2 - column_idx)
                    from_center_y = abs(dims[0] // 2 - row_idx)
                    dcolor = shadow_mult * (from_center_x * dx + from_center_y * dy)
                    color = clamp_rgb_add(color, dcolor)

                    rect = Rect(column_idx*cell_width, row_idx*cell_height, cell_width, cell_height)
                    draw.rect(self.bg, color, rect)


    def update_cursor(self, widget: Widget) -> None:
        if isinstance(widget, Entry):
            mouse.set_cursor(self.cursors["ibeam"])
        elif isinstance(widget, (Button, Checkbox, List, Slider)):
            mouse.set_cursor(self.cursors["hand"])
        else:
            mouse.set_cursor(self.cursors["arrow"])

    def render_all(self, widgets: dict) -> None:        
        self.cache = pg.Surface(self.screen_size, pg.SRCALPHA)
        # self.cache.fill((255, 255, 255))  # TODO A changer si c'est transparent 
        if self.bg:
            self.cache.blit(self.bg, (0, 0)) # TODO A changer si c'est transparent
        for widget in widgets.values():
            if not widget.is_visible:
                continue
            self.cache.blit(widget.surface, widget.pos)
            if isinstance(widget, AddonWidget) and (not isinstance(widget, List) or widget.list_shown):
                self.cache.blit(widget.addon_surface, widget.addon_pos)
