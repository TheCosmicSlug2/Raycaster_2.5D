from physics_engine.physics import get_dpos, pythagoras
from random import randint
from math import cos, sin, atan2
from audio import cyka


class Entity:
    def __init__(self, pos, textureids, speed, frames_oscillation=10, gopnik=False) -> None:
        self.posx, self.posy = pos
        self.texture_ids = textureids
        self.speed = speed
        self.tick_change = 0
        self.costume_idx = 0
        self.max_frames_oscillation = frames_oscillation
        self.isgopnik = gopnik
        if self.isgopnik:
            self.sound = cyka
            self.sound.play(-1)
    
    @property
    def texture_id(self):
        if self.tick_change > self.max_frames_oscillation:
            self.costume_idx = (self.costume_idx + 1) % len(self.texture_ids)
            self.tick_change = 0
        return self.texture_ids[self.costume_idx]
    
    @property
    def pos(self):
        return self.posx, self.posy

class EntityManager:
    def __init__(self, player, blyat_mode=False) -> None:
        self.player = player
        self.ennemies = [
            Entity((120, 120), [0, 1, 2, 3, 4, 5, 4, 3, 2, 1], 1.2, 3, True),
            Entity((120, 120), [0, 1, 2, 3, 4, 5, 4, 3, 2, 1], 0.8, 2, True),
            Entity((120, 120), [0, 1, 2, 3, 4, 5, 4, 3, 2, 1], 0.7, 4, True),
            Entity((120, 120), [0, 1, 2, 3, 4, 5, 4, 3, 2, 1], 1, 3, True),
            # Entity((120, 120), [5], 1.2),
            # Entity((120, 120), [6], 1),
            #Entity((120, 120), [0, 1], 0.5, 3)
        ] if blyat_mode else []

    def update(self):
        # Get pos in front of player

        dx, dy = cos(self.player.x_angle), sin(self.player.x_angle)
        target_pos = (self.player.posx + dx, self.player.posy + dy)
        for ent in self.ennemies:
            ent.tick_change += 1
            dx, dy = get_dpos(target_pos, ent.pos)
            if ent.isgopnik:
                used_dst = pythagoras(dx, dy) / 8
                ent.sound.set_volume(1/used_dst)
            if abs(dx) < 1 and abs(dy) < 1:
                continue

            # Calcul de l’angle vers le joueur
            angle = atan2(dy, dx)

            # Nouveau déplacement
            ent.posx += cos(angle) * ent.speed
            ent.posy += sin(angle) * ent.speed

    
    def get_ennemies(self):
        liste = []
        for ent in self.ennemies:
            dpos = get_dpos(self.player.pos, ent.pos)
            dst = pythagoras(dpos[0], dpos[1])
            liste.append(("ennemy", [(ent.pos, dst), ent.texture_id]))
        
        return liste