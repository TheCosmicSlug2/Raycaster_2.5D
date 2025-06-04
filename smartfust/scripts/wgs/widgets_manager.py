from smartfust.scripts.wgs.widget_renderer import WidgetRenderer
from smartfust.scripts.wgs.widgets import *
from smartfust.scripts.input_manager import *
from smartfust.scripts.physics import *


class WidgetManager:
    def __init__(self, widgets: dict[int: Widget]):
        self.widgets = widgets
        self.widget_renderer = WidgetRenderer()
        self.hover_widget = None
        self.focused_widget = None
        self.on_exit = False

    def reset_fonts(self, font_name: str) -> None:
        self.widget_renderer.reset_fonts(font_name)
        for widget in self.widgets.values():
            widget.surface = self.widget_renderer.get_widget_render(widget)

    def on_click(self) -> None: return

    def update_states(self, events: dict, last_events: dict) -> None:
        self.hover_widget = None
        for widget in self.widgets.values():
            if mouse_in_box(events[MOUSE_POS], widget.corners):
                self.hover_widget = widget
                widget.animate(1)
                widget.need_update = True
                continue
            if widget.animation_tick > 0 and not widget.clicked: # Didn't finished degrowth
                widget.animate(-1)
                widget.need_update = True

        if LEFTCLICK_UP in events:
            for widget in self.widgets.values():
                widget.on_click_animation(False)

        if LEFTCLICK_DOWN in events and LEFTCLICK_DOWN not in last_events:
            if self.hover_widget:
                self.focused_widget = self.hover_widget
                self.focused_widget.on_click_animation(True)
                self.focused_widget.on_click()
            else:
                self.hover_widget = None
                self.focused_widget = None


        if isinstance(self.focused_widget, Slider):
            if LEFTCLICK_DOWN in events:
                self.focused_widget.set_pos_to_mouse(events[MOUSE_POS][0])
                self.focused_widget.need_update = True

        if isinstance(self.focused_widget, Entry):
            if events.get(LEFT) and LEFT not in last_events:
                self.focused_widget.move(-1)
            if events.get(RIGHT) and RIGHT not in last_events:
                self.focused_widget.move(1)
            if events.get(BACKSPACE) and not BACKSPACE in last_events:
                self.focused_widget.remove_char()
            elif events[KEYS]:
                for key in events[KEYS]:
                    self.focused_widget.add_char(key)
            self.focused_widget.update_tick()
            self.focused_widget.need_update = True

        if isinstance(self.focused_widget, List):
            if DOWN in events and not DOWN in last_events and self.focused_widget.list_shown:
                self.focused_widget.move(1)
                self.focused_widget.need_update = True
            if UP in events and not UP in last_events and self.focused_widget.list_shown:
                self.focused_widget.move(-1)
                self.focused_widget.need_update = True
            if ENTER in events and not ENTER in last_events:
                self.focused_widget.list_shown = False
            if LEFTCLICK_DOWN in events and self.focused_widget.list_shown:
                if self.focused_widget.on_addon_click(events[MOUSE_POS]):
                    self.focused_widget.list_shown = False
                    self.focused_widget.need_update = True

        # Check if button is clicked
        if isinstance(self.focused_widget, Button) and self.focused_widget.return_value == "quit":
            self.on_exit = True


    def update_widget_surfaces(self) -> None:
        for widget in self.widgets.values():
            if not widget.need_update:
                continue
            widget.surface = self.widget_renderer.get_widget_render(widget)
            widget.need_update = False

        # Update cursor if current widget is entry
        if isinstance(self.focused_widget, Entry):
            widget.surface = self.widget_renderer.get_widget_render(widget)
