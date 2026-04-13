from physics_engine.physics import get_dpos, pythagoras
from random import randint
from math import cos, sin, atan2
from audio import cyka
from settings import EMPTY, FPS


class Entity:
    def __init__(self, pos, speed) -> None:
        self.posx, self.posy = pos
        self.speed = speed
        self.nature = None
    
    @property
    def pos(self):
        return self.posx, self.posy

class TextureEntity(Entity):
    def __init__(self, pos, textureids, speed, frames_oscillation=10) -> None:
        super().__init__(pos, speed)
        self.posx, self.posy = pos
        self.texture_ids = textureids
        self.speed = speed
        self.tick_change = 0
        self.costume_idx = 0
        self.max_frames_oscillation = frames_oscillation
    
    @property
    def texture_id(self):
        if self.tick_change > self.max_frames_oscillation:
            self.costume_idx = (self.costume_idx + 1) % len(self.texture_ids)
            self.tick_change = 0
        return self.texture_ids[self.costume_idx]
    
    @property
    def pos(self):
        return self.posx, self.posy

class PacGom(TextureEntity):
    def __init__(self, pos, speed, frames_oscillation=10) -> None:
        super().__init__(pos, textureids = [10], speed=speed, frames_oscillation=frames_oscillation)
    
    def update(self, target_pos):
        tx, ty = target_pos
        if abs(tx - self.posx) < 10 and abs(ty - self.posy) < 10:
            return True
        return False 


class Gopnik(TextureEntity):
    def __init__(self, pos, textureids, speed, frames_oscillation=10) -> None:
        super().__init__(pos, textureids, speed, frames_oscillation)
        self.sound = cyka
        self.sound.play(-1)
        self.nature = "gopnik"

class Ghost(TextureEntity):
    def __init__(self, gridpos, textureids, speed, level_master, frames_oscillation=10) -> None:
        self.level_master = level_master
        pos = ((gridpos[0] + 0.5) * self.level_master.cellw, (gridpos[1] + 0.5) * self.level_master.cellh)
        super().__init__(pos, textureids, speed, frames_oscillation)
        self.recalculate_tick = 0
        self.path = []
        self.current_idx_solving = 0
        self.nature = "ghost"
        self.last_target = (0,0)
        self.dir = (0, 0)
        self.threshold_path_update = FPS // 2
    
    @property
    def gridpos(self):
        return self.level_master.to_gridpos(self.pos)
    
    @property
    def offset_gridpos(self):
        multx = -1 if self.dir[0] > 0 else 1
        multy = -1
        return (
            int((self.posx + multx * self.level_master.cellw // 2) // self.level_master.cellw),
            int((self.posy + multy * self.level_master.cellh // 2) // self.level_master.cellh)
            )
    
    def update_path(self, player_pos):
        gridpos = self.level_master.to_gridpos(self.pos)
        endpos = self.level_master.to_gridpos(player_pos)

        if endpos == self.last_target:
            return

        self.last_target = endpos

        gridpos = self.level_master.to_gridpos(self.pos)
        self.path = self.level_master.solve_maze(gridpos, endpos, True)
        self.current_idx_solving = 0
    
    def update(self, target_pos):
        dx = target_pos[0] - self.posx
        dy = target_pos[1] - self.posy
        dist = (dx**2 + dy **2) ** 0.5
        # Si le ghost se trouve dans la même cellule, approche directe
        if dist < self.level_master.cellw:
            self.posx += (dx/dist) * self.speed
            self.posy += (dy/dist) * self.speed
            return
        # Sinon, appreoche en pathfinding
        if self.recalculate_tick % self.threshold_path_update == 0:
            self.update_path(target_pos)
        # Get the next grid position from the exit path
        self.recalculate_tick += 1
        next_path_idx = self.current_idx_solving + 1
        if next_path_idx >= len(self.path):
            return
        next_grid_pos = self.path[next_path_idx]

        gridpos = self.offset_gridpos
        # Calculate deltas
        new_dx = next_grid_pos[0] - gridpos[0]
        new_dy = next_grid_pos[1] - gridpos[1]
        self.dir = (new_dx, new_dy)

        self.posx += new_dx * self.speed
        self.posy += new_dy * self.speed


        if new_dx == 0 and new_dy == 0:
            target_x = next_grid_pos[0] * self.level_master.cellw
            target_y = next_grid_pos[1] * self.level_master.cellh

            dx = target_x - self.posx
            dy = target_y - self.posy

            if abs(dx) > self.speed:
                self.posx += self.speed if dx > 0 else -self.speed
            else:
                self.posx = target_x

            if abs(dy) > self.speed:
                self.posy += self.speed if dy > 0 else -self.speed
            else:
                self.posy = target_y

            return

        # si on a atteint la prochaine case → avancer dans le path
        if self.gridpos == next_grid_pos:
            self.current_idx_solving += 1

class ColorGhost(Ghost):
    def __init__(self, pos, textureids, speed, level_master, color, frames_oscillation=10) -> None:
        super().__init__(pos, textureids, speed, level_master, frames_oscillation)
        self.color = color
        if self.color == "yellow":
            self.threshold_path_update = 120
    
    def update(self, player_pos, player_dir):
        if self.color == "red":
            pos = player_pos
        if self.color == "pink":
            x, y = player_pos
            dirx, diry = player_dir
            pos = (x + 2 * cos(dirx) * self.level_master.cellw, y + 2 * sin(diry) * self.level_master.cellh)
        if self.color == "blue":
            x, y = player_pos
            dirx, diry = player_dir
            pos = (x - 2 * cos(dirx) * self.level_master.cellw, y - 2 * sin(diry) * self.level_master.cellh)
        if self.color == "yellow":
            pos = (randint(0, 20) * self.level_master.cellw, randint(0, 20) * self.level_master.cellh)
        super().update(pos)
                    

class EntityManager:
    def __init__(self, player, level_master, blyat_mode=False, pacman_mode=False) -> None:
        self.player = player
        self.level_master = level_master
        if blyat_mode:
            self.ennemies = blyat_ennemies = [
                    Gopnik((120, 120), [0, 1, 2, 3, 4, 5, 4, 3, 2, 1], 1.2, 3),
                    Gopnik((120, 120), [0, 1, 2, 3, 4, 5, 4, 3, 2, 1], 0.8, 2),
                    Gopnik((120, 120), [0, 1, 2, 3, 4, 5, 4, 3, 2, 1], 0.7, 4)
                ]
        elif pacman_mode:
            self.ennemies = [
                ColorGhost((10, 9), [6], 1, self.level_master, color="red"),
                ColorGhost((10, 9), [7], 1.2, self.level_master, color="yellow"),
                ColorGhost((10, 9), [8], 1.2, self.level_master, color="pink"),
                ColorGhost((10, 9), [9], 2, self.level_master, color="blue"),
                ] + self.get_pacgom_pos()
        else:
            self.ennemies = []
        self.ate_gom = False
        
    def get_pacgom_pos(self):
        pacgoms = []
        for i in range(self.level_master.mapw):
            for j in range(self.level_master.maph):
                if self.level_master.map_data[j][i].nature != EMPTY:
                    continue
                pacgoms.append(PacGom(((i + 0.5) * self.level_master.cellw, (j+0.5) * self.level_master.cellh), 0))
        self.nb_goms = len(pacgoms)
        return pacgoms

    def update(self):
        # Get pos in front of player

        dx, dy = cos(self.player.x_angle), sin(self.player.x_angle)
        target_pos = (self.player.posx + dx, self.player.posy + dy)
        for idx, ent in enumerate(self.ennemies):
            if ent.nature == "ghost":
                ent.update(target_pos, self.player.dir)
                continue
            if isinstance(ent, PacGom):
                if ent.update(target_pos):
                    self.ennemies.pop(idx)
                    self.ate_gom = True
                continue
            ent.tick_change += 1
            dx, dy = get_dpos(target_pos, ent.pos)
            if ent.nature == "gopnik":
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