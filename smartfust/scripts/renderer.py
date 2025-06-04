from pygame import cursors, time, Surface, draw, Rect, mouse, \
    SYSTEM_CURSOR_ARROW, SYSTEM_CURSOR_IBEAM, SYSTEM_CURSOR_HAND, display
from smartfust.scripts.wgs.widgets import *
from smartfust.scripts.colors.color import clamp_rgb_add

class Renderer:
    def __init__(self, screen):
        self.SCREEN = screen
        self.FPS = 30
        self.clock = time.Clock()
        self.bg = None

        self.cursors = {
            "arrow": cursors.Cursor(SYSTEM_CURSOR_ARROW),
            "ibeam": cursors.Cursor(SYSTEM_CURSOR_IBEAM),
            "hand": cursors.Cursor(SYSTEM_CURSOR_HAND)
        }

    def set_bg(self, type, dims, colors, array, shadow) -> None:
        self.bg = Surface(self.SCREEN.get_size())
        if type == "rgb":
            self.bg.fill(colors)
        if type == "chessboard":
            # Create array
            array = [[(column + row) % 2 for column in range(dims[0])] for row in range(dims[1])]

        if type in ("custom", "chessboard"):
            dims = (len(array[0]), len(array))
            cell_width = self.SCREEN.get_width() // dims[0]
            cell_height = self.SCREEN.get_height() // dims[1]
            shadow_sign = shadow["sign"]
            shadow_mult = shadow["mult"]
            dx = shadow_sign[0]
            dy = shadow_sign[1]
            dic = {i: color for i, color in enumerate(colors)}
            for row_idx, row in enumerate(array):
                for column_idx, column in enumerate(row):
                    color = dic[column]

                    from_center_x = abs(dims[1] // 2 - column_idx)
                    from_center_y = abs(dims[0] // 2 - row_idx)
                    dcolor = shadow_mult * (from_center_x * dx + from_center_y * dy)
                    color = clamp_rgb_add(color, dcolor)

                    rect = Rect(column_idx * cell_width, row_idx * cell_height, cell_width, cell_height)
                    draw.rect(self.bg, color, rect)


    def update_cursor(self, widget: Widget) -> None:
        if isinstance(widget, Entry):
            mouse.set_cursor(self.cursors["ibeam"])
        elif isinstance(widget, Button) or isinstance(widget, Checkbox):
            mouse.set_cursor(self.cursors["hand"])
        else:
            mouse.set_cursor(self.cursors["arrow"])

    def render_all(self, widgets: list[Widget]) -> None:
        self.SCREEN.fill((255, 255, 255))
        if self.bg:
            self.SCREEN.blit(self.bg, (0, 0))
        for widget in widgets.values():
            self.SCREEN.blit(widget.surface, widget.pos)
            if isinstance(widget, AddonWidget) and (not isinstance(widget, List) or widget.list_shown):
                self.SCREEN.blit(widget.addon_surface, widget.addon_pos)

    def update(self) -> None:
        display.flip()
        self.clock.tick(self.FPS)
