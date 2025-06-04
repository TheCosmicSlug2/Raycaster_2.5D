import pygame as pg
from settings import *
from math import pi

class InputHandler:
    def __init__(self, level_master) -> None:
        self.last_player_angle = 0
        self.sensitivity = 4
        self.previous_mouse_x = 0
        self.previous_mouse_y = 0
        self.level_master = level_master

        pg.mouse.set_pos(self.level_master.half_screen_dims)

    @staticmethod
    def get_mouse_event():
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "quit_game"

    @staticmethod
    def get_cmd_event(last_key):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "exit"
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    return "return"
                elif event.key == pg.K_BACKSPACE:
                    return "backspace"
                elif event.key == pg.K_UP or event.key == pg.K_DOWN:
                    continue
                else:
                    return event.unicode

        keys = pg.key.get_pressed()
        # the only keys that need constant check, to make it faster
        if keys[pg.K_UP]:
            return "up"
        if keys[pg.K_DOWN]:
            return "down"
        return ""


    @staticmethod
    def get_keyboard_events():
        keys = pg.key.get_pressed()

        dic_keys = {
            pg.K_s: "bas",
            pg.K_q: "gauche",
            pg.K_z: "haut",
            pg.K_d: "droite",
            pg.K_m: "map",
            pg.K_c: "cmd",
            pg.K_ESCAPE: "esc",
            pg.K_r : "r"
        }

        pressed_keys = []
        for key, value in dic_keys.items():
            if keys[key]:
                pressed_keys.append(value)

        return pressed_keys

    def center_mouse(self):
        mousex, mousey = pg.mouse.get_pos()
        if mousex < 50 or mousex > self.level_master.screen_dims[0] - 50:
            pg.mouse.set_pos(self.level_master.half_screen_dims[0], mousey)
        if mousey < 50 or mousey > self.level_master.screen_dims[1] - 50:
            pg.mouse.set_pos(mousex, self.level_master.screen_dims[1])

    def get_mouse_movement_since_last_frame(self) -> int:
        """Retourne l'angle du joueur en degrés basé sur la position de la souris (axe X uniquement)."""

        dx, dy = pg.mouse.get_rel()

        norm_dx = dx * pi / 180 / self.sensitivity
        norm_dy = dy * self.sensitivity

        self.center_mouse()

        return norm_dx, norm_dy
