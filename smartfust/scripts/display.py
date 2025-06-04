from pygame import display
from smartfust.scripts.input_manager import InputManager, EXIT
from smartfust.scripts.renderer import Renderer
from smartfust.scripts.wgs.widgets_manager import WidgetManager
from smartfust.scripts.wgs.widgets import Button, Checkbox, Entry, List, Slider, Widget


# Output code
GLOBAL_QUIT = 1
DISPLAY_QUIT = 2

class Display:
    def __init__(self,
                 screen: display=None,
                 dims: tuple=None,
                 title: str="Pygame Window",
                 widgets: dict = {}
                ):
        if not screen:
            if dims:
                screen = display.set_mode(dims)
            else:
                raise Exception("No display dimensions or classes")
        display.set_caption(title)
        self.renderer = Renderer(screen)
        self.widget_manager = WidgetManager(widgets)
        self.output_code = None

    def add_widgets(self, widgets: dict[int: Widget]):
        self.widget_manager.widgets.update(widgets)

    def mainloop(self) -> None:
        input_manager = InputManager()
        running = True
        while running:
            # Get input
            events = input_manager.get_events()

            if EXIT in events:
                self.output_code = GLOBAL_QUIT
                running = False

            self.widget_manager.update_states(events, input_manager.last_events)
            if self.widget_manager.on_exit:
                self.output_code = DISPLAY_QUIT
                running = False
            self.widget_manager.update_widget_surfaces()
            self.renderer.update_cursor(self.widget_manager.hover_widget)

            input_manager.set_last_events()

            self.renderer.render_all(self.widget_manager.widgets)
            self.renderer.update()

    def set_font(self, font_name: str) -> None:
        self.widget_manager.reset_fonts(font_name)

    def set_bg(self,
               type: str="rgb",
               dims: tuple=None,
               colors: int | tuple=None,
               array: list=None,
               shadow: dict={"sign": (0, 0), "mult": 3}
               ) -> None:
        """
        Type : rgb | chessboard | custom
        """
        self.renderer.set_bg(type, dims, colors, array, shadow)

    def get_output(self) -> dict:
        dic = {}
        if self.output_code == GLOBAL_QUIT:
            return self.output_code
        for widget_id, widget in self.widget_manager.widgets.items():
            value = None
            if isinstance(widget, Button):
                value = widget.clicked
            if isinstance(widget, Checkbox):
                value = widget.state
            if isinstance(widget, Entry):
                value = widget.inner_text
            if isinstance(widget, List):
                value = widget.current_value
            if isinstance(widget, Slider):
                value = widget.value
            dic[widget_id] = value
        return dic


