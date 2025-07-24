from math import pi, sqrt
from random import choice
from physics_engine.physics import trouver_longueurs_trigo, check_4_side_collision
from settings import PLAYER_DIMS, HALF_SCREEN_DIMS, FOV_MAX_DEG, FPS, player_side_size

class Player:
    def __init__(self, level_master, far_spawn=False):
        self.level_master = level_master
        self.far_spawn = far_spawn
        self.dims = PLAYER_DIMS
        self.x_angle = 0
        self.y_angle = HALF_SCREEN_DIMS[1]
        self.reset_position()
        self.set_angle()
        self.rect_sprite = None
        self.is_moving = False
        self.fov = FOV_MAX_DEG * (pi / 180)
        self.speed = sqrt(self.level_master.cellw * self.level_master.cellh) / (FPS / 2)
        self.hit_nature = 0

    @property
    def width(self):
        return self.dims[0]

    @property
    def height(self):
        return self.dims[1]

    def reset_position(self):
        if self.far_spawn:
            self.gridpos = self.level_master.player_starting_pos
        else:
            self.goto_random_location()
    
    def get_hit_nature(self, x, y):
        checks = (
            (x, y),
            (x + self.width, y),
            (x, y + self.height),
            (x + self.width, y + self.height)
        )

        for x, y in checks:
            cell = self.level_master.get_at(x, y)
            if not cell:
                continue
            if cell.nature == 0:
                continue
            return cell.nature # First collision, not all

    def move(self, mvt_dir) -> None:
        """ Déplace le joueur selon un angle """
        self.is_moving = True
        lg_x, lg_y = trouver_longueurs_trigo(self.x_angle + mvt_dir)
        next_x, next_y = self.posx + (lg_x * self.speed), self.posy + (lg_y * self.speed)
        # si le movement suivant collide un mur
        if check_4_side_collision(
            top_left_pos=(next_x, next_y),
            object_dims=self.dims,
            cell_dims=self.level_master.cell_dims,
            map_data=self.level_master.map_data,
            map_data_dims=self.level_master.grid_dims
            ):
            self.hit_nature = self.get_hit_nature(next_x, next_y)
            self.is_moving = False
            return
        self.posx, self.posy = next_x, next_y
        self.check_collisions_border()

    def check_collisions_border(self) -> None:
        """ Checke les collisions avec les bordures de la carte """
        # collisions horizontales
        self.posx = max(0, min(self.posx, self.level_master.screenw - self.width))
        # collisions verticales
        self.posy = max(0, min(self.posy, self.level_master.screenh - self.height))

    def update_x_angle(self, add_x):
        self.x_angle += add_x

        if self.x_angle < 0:
            self.x_angle += 2 * pi
        if self.x_angle > 2 * pi:
            self.x_angle -= 2 * pi

    def update_y_angle(self, add_y):
        self.y_angle = min(max(self.y_angle + add_y, 0), self.level_master.screenh)

    @property
    def pos(self):
        return self.posx, self.posy

    @pos.setter
    def pos(self, _pos):
        self.posx, self.posy = _pos

    @property
    def gridposx(self):
        return int(self.posx // self.level_master.cellw)

    @gridposx.setter
    def gridposx(self, _gridx):
        self.posx = self.level_master.cellw * (_gridx + 0.5) - PLAYER_DIMS[0] // 2

    @property
    def gridposy(self):
        return int(self.posy // self.level_master.cellh)

    @gridposy.setter
    def gridposy(self, _gridy):
        self.posy = self.level_master.cellh * (_gridy + 0.5) - PLAYER_DIMS[1] // 2

    @property
    def gridpos(self):
        return (self.gridposx, self.gridposy)

    @gridpos.setter
    def gridpos(self, _gripos):
        self.gridposx, self.gridposy = _gripos

    def goto_random_location(self):
        # Get empty cells
        startposes = []
        for row_idx, row in enumerate(self.level_master.map_data):
            for col_idx, cell in enumerate(row):
                if not cell.nature:
                    startposes.append((col_idx, row_idx))
        self.gridpos = choice(startposes)


    def set_angle(self):
        # Met à jour l'orientation, pour que le joue soit toujours face à un couloir
        neighbour_cells = {
            (1, 0): 0,
            (0, 1): pi/2,
            (-1, 0): pi,
            (0, -1): -pi/2,    # Un peu cursed ces coordonnés, à revoir + tard
        }
        for relative_position, angle in neighbour_cells.items():
            nei_abs_x = self.gridposx + relative_position[0]
            nei_abs_y = self.gridposy + relative_position[1]
            if nei_abs_y > len(self.level_master.map_data) - 1:
                continue
            if nei_abs_x > len(self.level_master.map_data[nei_abs_y]) - 1:
                continue
            if self.level_master.map_data[nei_abs_y][nei_abs_x].nature == 0:
                self.x_angle = angle
                return

    def set_pos(self, pos: tuple):
        self.posx = pos[0] - player_side_size // 2
        self.posy = pos[1] - player_side_size // 2
    
    def reset_vars(self):
        self.hit_nature = 0
        self.is_moving = False
