from ctypes import Array
import pygame as pg
from smartfust.scripts.input_manager import InputManager, EXIT
from smartfust.scripts.renderer import Renderer
from smartfust.scripts.wgs.widgets_manager import WidgetManager
from smartfust.scripts.wgs.widgets import Button, Checkbox, Entry, List, Slider, Widget
from smartfust.scripts.param_types import *



# Output code
GLOBAL_QUIT = 1
DISPLAY_QUIT = 2

class WrongDimensions(Exception):
    pass

class WrongArguments(Exception):
    pass

class Display:
    def __init__(self,
                 screen: Optional[pg.Surface]=None,
                 dims: Optional[DIMS]=None,
                 title: Optional[str]="",
                 widgets: dict = {}
                ):
        if not screen and not dims:
            raise WrongArguments("Provide ether a screen or dimensions")
        if screen and dims:
            raise WrongArguments("Do not provide an already existing screens and dims")
        if dims:
            self.screen = pg.display.set_mode(dims)
        else:
            self.screen = screen
        
        if title:
            pg.display.set_caption(title)
        self.renderer = Renderer(self.screen.get_size())
        self.widget_manager = WidgetManager(widgets)
        self.input_manager = InputManager()
        self.clock = pg.time.Clock()
        self.output_code = None

    def add_widgets(self, widgets: dict[int, Widget]):
        self.widget_manager.widgets.update(widgets) # "update" ici dans le cadre d'un dictionnaire
    
    def update(self, pg_events):
        events = self.input_manager.get_events(pg_events)
        if EXIT in events:
            self.output_code = GLOBAL_QUIT
            return False

        self.widget_manager.update_states(events, self.input_manager.last_events)
        if self.widget_manager.on_exit:
            self.output_code = DISPLAY_QUIT
            self.reset()
            return False
        self.widget_manager.update_widget_surfaces()
        self.renderer.update_cursor(self.widget_manager.hover_widget)

        self.input_manager.set_last_events()
        self.renderer.render_all(self.widget_manager.widgets)
        self.screen.blit(self.renderer.cache, (0, 0))
        return True

    def mainloop(self) -> None:
        running = True
        while running:
            events = pg.event.get()
            running = self.update(events)
            pg.display.flip()
            self.clock.tick(30)
    
    def reset(self):
        self.widget_manager.on_exit = False
        self.widget_manager.focused_widget = None

    def set_font(self, font_name: str) -> None:
        self.widget_manager.reset_fonts(font_name)

    def set_bg(self,
               _type: str="rgb",
               dims: Optional[DIMS] = None,
               colors: Optional[Union[int, RGB]] = None,
               array: Optional[INT_2D_ARRAY] = None,
               image_path: Optional[str] = None, 
               shadow: dict={"sign": (0, 0), "mult": 3}
               ) -> None:
        """
        Type : none | rgb | chessboard | custom
        """
        self.renderer.set_bg(_type, dims, colors, array, image_path, shadow)

    def widget_values(self) -> dict:
        dic = {}
        for widget_id, widget in self.widget_manager.widgets.items():
            dic[widget_id] = widget.get_value()
        return dic
    
    def set_title(self, new_title):
        pg.display.set_caption(new_title)

    def change_widget(self, widget_id, new_text):
        self.widget_manager.change_widget(widget_id, new_text)
    
    def hide_widget(self, widget_id):
        self.widget_manager.hide_widget(widget_id)
    
    def hide_all_widgets(self):
        self.widget_manager.hide_all_widgets()

    def show_widget(self, widget_id):
        self.widget_manager.show_widget(widget_id)
        
    def show_all_widgets(self):
        self.widget_manager.show_all_widgets()
    
    def set_display_size(self, size):
        self.renderer = Renderer(size)
