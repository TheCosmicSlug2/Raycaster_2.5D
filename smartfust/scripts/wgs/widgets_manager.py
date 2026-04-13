from tkinter import Label
from typing import Optional
from smartfust.scripts.wgs.widget_renderer import WidgetRenderer
from smartfust.scripts.wgs.widgets import Widget, Slider, Entry, Button, List, Label
from smartfust.scripts.input_manager import LEFTCLICK_UP, LEFTCLICK_DOWN, MOUSE_POS, LEFT,\
    RIGHT, BACKSPACE, KEYS, DOWN, UP, ENTER, SCROLL_UP, SCROLL_DOWN
from smartfust.scripts.physics import *


class WidgetManager:
    def __init__(self, widgets: dict[int, Widget]):
        self.widgets = widgets
        self.widget_renderer = WidgetRenderer()
        self.hover_widget: Optional[Widget] = None
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
            if not widget.is_visible:
                continue
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
            if self.focused_widget:
                self.focused_widget.dehover()
            if self.hover_widget:
                self.focused_widget = self.hover_widget
                self.focused_widget.on_click_animation(True)
                self.focused_widget.on_click()
            else:
                self.hover_widget = None
                self.focused_widget = None


        if isinstance(self.focused_widget, Slider):
            if LEFTCLICK_DOWN in events:
                self.focused_widget.set_pos_to_mouse(events[MOUSE_POS])
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
            CAN_SCROLL_UP = (UP in events or SCROLL_UP in events) and \
                not (UP in last_events or SCROLL_UP in last_events)
            CAN_SCROLL_DOWN = (DOWN in events or SCROLL_DOWN in events) and \
                not (DOWN in last_events or SCROLL_DOWN in last_events)

            if CAN_SCROLL_DOWN and self.focused_widget.list_shown:
                self.focused_widget.move(1)
                self.focused_widget.need_update = True
            if CAN_SCROLL_UP and self.focused_widget.list_shown:
                self.focused_widget.move(-1)
                self.focused_widget.need_update = True
            if ENTER in events and not ENTER in last_events:
                self.focused_widget.list_shown = False
            if LEFTCLICK_DOWN in events and self.focused_widget.list_shown:
                self.focused_widget.check_addon_click(events[MOUSE_POS])
            else:
                self.focused_widget.scrollbar_clicked = False

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
            self.focused_widget.surface = self.widget_renderer.get_widget_render(self.focused_widget)
    
    def change_widget(self, widget_id, new_text):
        widget = self.widgets[widget_id]
        if isinstance(widget, Label):
            widget.text = new_text
            widget.need_update = True
    
    def hide_widget(self, widget_id):
            self.widgets[widget_id].is_visible = False
        
    def hide_all_widgets(self):
        for widget_id in self.widgets:
            self.hide_widget(widget_id)

    def show_widget(self, widget_id):
            self.widgets[widget_id].is_visible = True
        
    def show_all_widgets(self):
        for widget_id in self.widgets:
            self.show_widget(widget_id)
