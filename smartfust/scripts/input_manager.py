from pygame import event, MOUSEBUTTONUP, KEYDOWN, mouse, K_LEFT, K_RIGHT, K_UP, K_DOWN, K_BACKSPACE, K_RETURN, key, QUIT

# Events
EXIT = 1
LEFTCLICK_DOWN = 2
LEFTCLICK_UP = 3
RIGHTCLICK_DOWN = 4
RIGHTCLICK_UP = 5
LEFT = 6
UP = 7
RIGHT = 8
DOWN = 9
MOUSE_POS = 10
KEYS = 11
BACKSPACE = 12
ENTER = 13

class InputManager:
    def __init__(self):
        self.events = {}
        self.last_events = {}

    def get_events(self):
        # Pygame events
        self.events[KEYS] = []
        for e in event.get():
            if e.type == QUIT:
                self.events[EXIT] = True
            if e.type == MOUSEBUTTONUP:
                if e.button == 1:
                    self.events[LEFTCLICK_UP] = e.pos
                if e.button == 3:
                    self.events[RIGHTCLICK_UP] = e.pos
            if e.type == KEYDOWN:
                if e.unicode:
                    self.events[KEYS] = e.unicode

        # Mouse pos and click
        mouse_pressed = mouse.get_pressed()
        if mouse_pressed[0]:
            self.events[LEFTCLICK_DOWN] = True
        if mouse_pressed[2]:
            self.events[RIGHTCLICK_DOWN] = True
        self.events[MOUSE_POS] = mouse.get_pos()

        desired_keys = {
            K_LEFT: LEFT,
            K_RIGHT: RIGHT,
            K_UP: UP,
            K_DOWN: DOWN,
            K_BACKSPACE: BACKSPACE,
            K_RETURN: ENTER
        }

        keys = key.get_pressed()
        for k, value in desired_keys.items():
            if keys[k]:
                self.events[value] = True

        return self.events

    def set_last_events(self):
        self.last_events = self.events
        self.events = {}
