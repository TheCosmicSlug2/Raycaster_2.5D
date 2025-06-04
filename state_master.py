from settings import ticks_to_update_map, ticks_to_update_mouse, ticks_to_update_solving, FPS

class StateMaster:
    def __init__(self) -> None:
        self.map_shown = False
        self.tick_map_update = 0
        self.mouse_visible = False
        self.tick_mouse_visible = 0
        self.global_tick = 0
        self.tick_solving = 0
        self.solving = False

    @staticmethod
    def check_update_possible(tick, threshold):
        return tick >= threshold

    @staticmethod
    def toggle_state(state):
        return not state

    @staticmethod
    def reset_tick():
        return 0

    def check_map_update_possible(self):
        if not self.check_update_possible(self.tick_map_update, ticks_to_update_map):
            return
        self.tick_map_update = self.reset_tick()
        self.map_shown = self.toggle_state(self.map_shown)

    def check_mouse_update_possible(self):
        if not self.check_update_possible(self.tick_mouse_visible, ticks_to_update_mouse):
            return
        self.tick_mouse_visible = self.reset_tick()
        self.mouse_visible = self.toggle_state(self.mouse_visible)

    def check_solving_update_possible(self):
        if not self.check_update_possible(self.tick_solving, ticks_to_update_solving):
            return False
        self.tick_solving = self.reset_tick()
        self.solving = self.toggle_state(self.solving)
        return True

    def update_tick(self, tick):
        tick += 1
        if tick > FPS * 5:
            return FPS
        return tick

    def update(self):
        self.tick_map_update = self.update_tick(self.tick_map_update)
        self.tick_mouse_visible = self.update_tick(self.tick_mouse_visible)
        self.tick_solving = self.update_tick(self.tick_solving)
        self.global_tick += 1
