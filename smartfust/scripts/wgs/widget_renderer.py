from pygame import draw, font, Rect, SRCALPHA, Surface
from smartfust.scripts.wgs.widgets import *

class WidgetRenderer:
    def __init__(self):
        font.init()
        self.fonts = {}
        self.current_font = "Times New Roman"

    def reset_fonts(self, font_name: str):
        self.current_font = font_name
        for font_height in self.fonts.keys():
            self.add_font(font_height)

    def add_font(self, height: int):
        self.fonts[height] = font.SysFont(self.current_font, height)

    def get_font(self, height: float | int):
        if height not in self.fonts:
            height = int(height)
            self.add_font(height)
        return self.fonts[height]


    def get_widget_render(self, widget: Widget) -> Surface:
        width, height = widget.dims
        tot_borx, tot_bory = 0, 0
        outer_surface = Surface(widget.dims, SRCALPHA)
        outer_surface.fill(widget.colors[0].rgba)
        for color, border in zip(widget.colors[1:], widget.borders):
            color = color.rgba
            width = width - 2 * border
            height = height - 2 * border
            tot_borx += border
            tot_bory += border
            inner_surface = Surface((width, height), SRCALPHA)
            inner_surface.fill(color)
            outer_surface.blit(inner_surface, (tot_borx, tot_bory))
        if isinstance(widget, AddonWidget):
            # Create addon surface
            widget.addon_surface = Surface((widget.addon_dims), SRCALPHA)
        if isinstance(widget, TextureWidget):
            if widget.texture:
                sx = widget.texture.get_width()
                sy = widget.texture.get_height()
                x = (outer_surface.get_width() - sx) / 2
                y = (outer_surface.get_height() - sy) / 2
                outer_surface.blit(widget.texture, (x, y))

        if isinstance(widget, Label) or isinstance(widget, Button):
            font = self.get_font(widget.text_height)
            text_render = font.render(widget.text, True, widget.textfg, None)

            half_x = (widget.width - text_render.get_width()) / 2
            half_y = (widget.height - text_render.get_height()) / 2
            outer_surface.blit(text_render, (half_x, half_y))
        if isinstance(widget, Checkbox) and widget.state == True:
            inner_surface.fill(widget.check_color.rgba)
            outer_surface.blit(inner_surface, (tot_borx, tot_bory))
        if isinstance(widget, Entry):
            text = widget.get_visible()
            font = self.get_font(widget.text_height)
            text_render = font.render(text, True, (0, 0, 0))
            widget.text_width = text_render.get_width()
            outer_surface.blit(text_render, (tot_borx + 2, widget.y_margin))
            # Blit cursor
            if widget.cursor_state:
                # Create temporary render to get a good position
                temp_rend = font.render(text[:widget.cursorx], True, (0, 0, 0))
                cursor_rect = Rect(temp_rend.get_width() + tot_borx, widget.y_margin / 2 + tot_bory, 2, widget.text_height)
                draw.rect(outer_surface, (0, 0, 0), cursor_rect)
        if isinstance(widget, Slider):
            # Draw slider bar :
            rect = Rect(widget.bar_x + tot_borx, tot_bory, widget.bar_width, widget.height - tot_bory * 2)
            rect2 = Rect(widget.bar_x + tot_borx + 2, tot_bory + 2, widget.bar_width - 4, widget.height - tot_bory * 2 - 4)
            draw.rect(outer_surface, (150, 150, 150), rect)
            draw.rect(outer_surface, (120, 120, 120), rect2)
            font = self.get_font(widget.text_height)
            render = font.render(str(widget.value), True, widget.bar_text_fg)
            widget.addon_surface.blit(
                render,
                (widget.bar_x + tot_borx + (rect.width - render.get_width()) // 2,
                 tot_bory + (rect.height - render.get_height())))
        if isinstance(widget, List):
            text = str(widget.current_value)
            font = self.get_font(widget.text_height)
            text_render = font.render(text, True, (0, 0, 0))
            outer_surface.blit(text_render, (tot_borx + 2, (widget.height - text_render.get_height()) / 2))

            # fill addon surface
            y = 0
            for value_idx, value in widget.get_visible().items():
                bg_color = (0, 0, 255) if value_idx == widget.y else (240, 240, 240)
                fg_color = (255, 255, 255) if value_idx == widget.y else (0, 0, 0)
                small_rect = Surface(widget.dims)
                small_rect.fill(bg_color)
                text_render = font.render(value, False, fg_color, bg_color)
                widget.addon_surface.blit(small_rect, (0, y*widget.height))
                widget.addon_surface.blit(text_render, (widget.tot_border, y * widget.height + (widget.height - text_render.get_height()) // 2))
                y += 1
        return outer_surface
