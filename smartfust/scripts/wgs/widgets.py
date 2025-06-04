from smartfust.scripts.colors.color import Color
from smartfust.scripts.colors.color_list import BLACK, GREEN, WHITE
from smartfust.scripts.physics import *

DEFAULT = 1

class Widget:
    def __init__(
            self,
            pos: tuple[int],
            dims: tuple[int],
            colors: list[tuple]=[BLACK, WHITE],
            borders: list[int]=[3]
            ):
        self.posx, self.posy = pos
        self.width, self.height = dims
        self.colors = [Color(color) for color in colors]
        self.borders = borders
        self.surface = None
        self.need_update = True
        self.clicked = False
        self.animation_tick = 0
        self.max_anim = 5

    @property
    def tot_border(self):
        return sum(self.borders)

    @property
    def pos(self):
        return self.posx, self.posy

    @property
    def dims(self):
        return self.width, self.height

    @property
    def corners(self):
        return (
            self.posx,
            self.posx + self.width,
            self.posy,
            self.posy + self.height
        )

    @property
    def rect(self):
        return (
            self.posx,
            self.posy,
            self.width,
            self.height
        )

    def animate(self, state):
        return

    def on_click_animation(self, state):
        return

    def on_click(self):
        return

    @property
    def can_animate(self):
        return 0 < self.animation_tick < self.max_anim

class TextureWidget(Widget):
    def __init__(self,
                 pos,
                 dims,
                 texture=None,
                 colors=[BLACK, WHITE],
                 borders=[3]):
        super().__init__(pos, dims, colors, borders)
        self.texture = texture

    def set_texture(self, texture):
        self.texture = texture


class TextWidget(Widget):
    def __init__(self,
                 pos,
                 dims,
                 text,
                 textfg=BLACK,
                 font=DEFAULT,
                 text_height=10,
                 colors=[BLACK, WHITE],
                 borders=[3]
                ):
        super().__init__(pos, dims, colors, borders)
        self.text = text
        self.textfg = textfg
        self.font = font
        self.text_height = text_height

class Label(TextWidget):
    def __init__(self,
                 pos,
                 dims,
                 text,
                 textfg=BLACK,
                 font=DEFAULT,
                 text_height=10,
                 colors=[BLACK, WHITE],
                 borders=[3]
                 ):
        super().__init__(pos, dims, text, textfg, font, text_height, colors, borders)

class Button(TextWidget):
    def __init__(self,
                 pos,
                 dims,
                 text,
                 return_value=None,
                 textfg=BLACK,
                 font=DEFAULT,
                 text_height=10,
                 colors=[BLACK, WHITE],
                 borders=[3],
                 animation: dict={"color": -6}):
        super().__init__(pos, dims, text, textfg, font, text_height, colors, borders)
        self.return_value = return_value
        self.animation = animation
        if "duration" in animation:
            self.max_anim = animation["duration"]

    def set_hover_animation(self, type: dict):
        self.animation = type

    def animate(self, state: int):
        if state == 1 and self.animation_tick >= self.max_anim:
            return
        if state == -1 and self.animation_tick <= 0:
            return

        sign = state
        if "size" in self.animation:
            addx, addy = self.animation["size"]
            dx = addx * sign
            dy = addy * sign
            self.width += dx
            self.height += dy
            self.posx -= dx / 2
            self.posy -= dy / 2
            self.text_height += sign * 0.4
            self.borders = [i + sign / 16 for i in self.borders]
        if "color" in self.animation:
            add = self.animation["color"]
            dx = add * sign
            for color in self.colors:
                color.add(dx)
        self.animation_tick += sign

    def on_click_animation(self, state):
        if state == True or (state == False and self.clicked):
            for color in self.colors:
                color.invert()
            self.need_update = True

        self.clicked = state

class Checkbox(Widget):
    def __init__(self, pos, dims, check_color=GREEN, colors=[BLACK, WHITE], borders=[3]):
        super().__init__(pos, dims, colors, borders)
        self.check_color = Color(check_color)
        self.state = False

    def switch_state(self):
        self.state = not self.state
        self.need_update = True

    def animate(self, state: int):
        if state == 1 and self.animation_tick >= self.max_anim:
            return
        if state == -1 and self.animation_tick <= 0:
            return

        sign = state
        add = 3
        dx = add * sign
        for color in self.colors:
            color.add(dx)
        self.animation_tick += sign

    def on_click(self):
        self.switch_state()

class Entry(Widget):
    def __init__(self,
                 pos,
                 dims,
                 colors=[BLACK, WHITE],
                 borders=[3],
                 inner_text=""
                ):
        super().__init__(pos, dims, colors, borders)
        self.inner_text = inner_text
        self.cursorx = len(self.inner_text)
        self.scrollx = 0
        self.cursor_state = True
        # text ratio : 8 width -> 30 height
        self.x_threshold = sum(borders) * 4
        self.y_margin = self.tot_border + 2
        self.text_height = self.height - self.y_margin * 2
        self.text_width = 0
        self.tick = 0

    @property
    def cursor_at_end(self):
        return self.cursorx == len(self.inner_text)

    def move(self, side: int) -> None:
        self.cursorx = max(0, min(self.cursorx + side, len(self.inner_text)))

    def update_tick(self) -> None:
        self.cursor_state = self.tick % 30 < 15
        self.tick += 1

    def add_char(self, char: str) -> None:
        self.inner_text = self.inner_text[:self.cursorx] + char + self.inner_text[self.cursorx:]
        self.cursorx += 1
        if self.cursor_at_end and self.text_width > self.width - self.x_threshold:
            self.scrollx += 2
        self.cursor_state = True

    def remove_char(self) -> None:
        if self.inner_text == "":
            return
        if self.cursorx == 0:
            return
        self.inner_text = self.inner_text[:self.cursorx-1] + self.inner_text[self.cursorx:]
        self.cursorx = max(0, self.cursorx - 1)
        self.scrollx = max(0, self.scrollx - 1)
        self.cursor_state = True

    def get_visible(self) -> str:
        return self.inner_text[self.scrollx:]


class AddonWidget(Widget):
    def __init__(self, pos, dims, addon_pos, addon_dims, colors=[BLACK, WHITE], borders=[3]):
        super().__init__(pos, dims, colors, borders)
        self.addon_surface = None
        self.addon_posx, self.addon_posy = addon_pos
        self.addon_width, self.addon_height = addon_dims

    def on_addon_click(self, mouse_pos): return

    @property
    def addon_corners(self):
        return (
            self.addon_posx,
            self.addon_posx + self.addon_width,
            self.addon_posy,
            self.addon_posy + self.addon_height
        )

    @property
    def addon_rect(self) -> tuple:
        return (
            self.addon_posx,
            self.addon_posy,
            self.addon_width,
            self.addon_height
        )

    @property
    def addon_dims(self) -> tuple:
        return self.addon_width, self.addon_height

    @property
    def addon_pos(self) -> tuple:
        return self.addon_posx, self.addon_posy

class Slider(AddonWidget):
    def __init__(self, pos, dims, range=(0, 100), default_value=None, text_height=None, bar_text_fg=BLACK, colors=[BLACK, WHITE], borders=[3]):
        ad_dims = dims
        ad_pos = (pos[0], pos[1] - dims[1])
        super().__init__(pos, dims, ad_pos, ad_dims, colors, borders)

        if not text_height:
            text_height = self.height // 2
        self.bar_text_fg = bar_text_fg
        self.text_height = text_height
        self.min, self.max = range
        self.drange = self.max - self.min
        if not default_value:
            default_value = (self.max + self.min) // 2
        self.value = default_value
        self.dx = self.width / self.max
        self.bar_width = 20
        self.bar_x = 0
        self.set_pos_from_value(self.value)

    @property
    def slidebar_rect(self):
        x1 = self.posx + self.bar_x
        x2 = x1 + self.width
        y1 = self.posy
        y2 = self.posy + self.height
        return x1, x2, y1, y2

    def get_mousex_ratio(self, mouse_x: int) -> float:
        relative_mousex = mouse_x - (self.posx + self.tot_border + self.bar_width // 2)
        tot_width = self.width - (self.tot_border * 2 + self.bar_width)
        ratio = relative_mousex / tot_width
        if ratio < 0:
            return 0
        if ratio > 1:
            return 1
        return ratio

    def set_pos_to_mouse(self, mousex: int):
        ratio = self.get_mousex_ratio(mousex)
        self.value = int(self.drange * ratio) + self.min
        self.set_pos_from_value(self.value)

    def set_pos_from_value(self, value: int):
        ratio = (value - self.min) / self.drange
        tot = self.width - (self.tot_border * 2 + self.bar_width)
        self.bar_x = tot * ratio # TODO : généraliser

class List(AddonWidget):
    def __init__(self, pos, dims, text_height=None, values=[], colors=[BLACK, WHITE], borders=[3]):
        self.max_visible = 5
        addon_pos = (pos[0], pos[1] + dims[1])
        addon_dims = (dims[0], dims[1] * self.max_visible)
        super().__init__(pos, dims, addon_pos, addon_dims, colors, borders)
        if not values:
            values = ["value" + str(i) for i in range(10)]
        self.values = values

        y_margin = self.tot_border + 4 # 3 est arbitraire
        if not text_height:
            text_height = self.height - y_margin * 2
        self.text_height = text_height
        self.y = 0
        self.scroll_y = 0
        self.list_shown = False
        self.current_value = self.values[self.y]

    def on_addon_click(self, mouse_pos: tuple):
        if not mouse_in_box(mouse_pos, self.addon_corners):
            return False
        # Find relative mouse pos
        relative_posy = mouse_pos[1] - (self.posy + self.height)
        idx = max(0, min(relative_posy // self.height, self.max_visible))
        self.set_y(self.scroll_y + idx)
        self.scroll_y = max(0, min(self.y - self.max_visible + 3, len(self.values) - self.max_visible))
        return True

    @property
    def corners(self):
        if not self.list_shown:
            return super().corners

        return (
            self.posx,
            self.posx + self.width,
            self.posy,
            self.posy + self.height + self.addon_height
        )

    def set_y(self, y: int):
        self.y = y
        self.current_value = self.values[self.y]

    def on_click(self):
        self.list_shown = True

    def move(self, side: int):
        self.set_y(max(0, min(self.y + side, len(self.values) - 1)))
        if self.y - self.scroll_y > self.max_visible - 1: # Scroll down
            self.scroll_y += 1
        if self.y - self.scroll_y < 0: # Scroll up
            self.scroll_y -= 1

    def get_visible(self):
        values = self.values[self.scroll_y:self.scroll_y + self.max_visible]
        return {self.scroll_y + i: value for i, value in enumerate(values)}
