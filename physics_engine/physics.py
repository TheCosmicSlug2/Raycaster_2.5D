from math import cos, sin, radians, sqrt, pi
from settings import *

class Physics:
    def __init__(self) -> None:
        self.forward = radians(0)
        self.right = radians(90)
        self.backward = radians(180)
        self.left = radians(270)


        self.dirs = (self.right, self.forward, self.left, self.backward)
        self.delta_to_dir = {
            (-1, 0): self.backward,
            (1, 0): self.forward,
            (0, -1): self.left,
            (0, 1): self.right
        }

    @staticmethod
    def trouver_longueurs_trigo(loc_angle_degres: int) -> tuple:
        """ Convertit un angle en radian et renvoie son sinus et cosinus """
        angle_radians = radians(loc_angle_degres)
        x = cos(angle_radians)
        y = sin(angle_radians)
        return x, y


    @staticmethod
    def trouver_longueurs_trigo(rad: int) -> tuple:
        """ Convertit un angle en radian et renvoie son sinus et cosinus """
        x = cos(rad)
        y = sin(rad)
        return x, y

    @staticmethod
    def check_4_side_collision(top_left_pos, object_dims, cell_dims, map_data, map_data_dims) -> bool:
        """ Putain c'est chiant les collisions """

        # La "vrai" position du joueur est invisible
        top_left_pos = (round(top_left_pos[0]), round(top_left_pos[1]))

        # Obtenir la position absolue des 4 côtés
        top_right_pos = (top_left_pos[0] + object_dims[0], top_left_pos[1])
        bottom_left_pos = (top_left_pos[0], top_left_pos[1] + object_dims[1])
        bottom_right_pos = (top_right_pos[0], bottom_left_pos[1])

        cell_top_left_pos = (top_left_pos[0] // cell_dims[0], top_left_pos[1] // cell_dims[1])
        cell_top_right_pos = (top_right_pos[0] // cell_dims[0], top_left_pos[1] // cell_dims[1])
        cell_bottom_left_pos = (bottom_left_pos[0] // cell_dims[0], bottom_left_pos[1] // cell_dims[1])
        cell_bottom_right_pos = (bottom_right_pos[0] // cell_dims[0], bottom_right_pos[1] // cell_dims[1])

        if cell_top_left_pos[0] < 0 or cell_top_left_pos[1] < 0:
            return True

        if cell_bottom_right_pos[0] > map_data_dims[0] - 1 or cell_bottom_right_pos[1] > map_data_dims[1] - 1:
            return True

        cell_top_left = map_data[cell_top_left_pos[1]][cell_top_left_pos[0]]
        cell_top_right = map_data[cell_top_right_pos[1]][cell_top_right_pos[0]]
        cell_bottom_left = map_data[cell_bottom_left_pos[1]][cell_bottom_left_pos[0]]
        cell_bottom_right = map_data[cell_bottom_right_pos[1]][cell_bottom_right_pos[0]]

        return cell_top_left.nature in (1,3) or cell_top_right.nature in (1,3) or cell_bottom_left.nature in (1,3) or cell_bottom_right.nature in (1,3)


    @staticmethod
    def get_color_collided(top_left_pos, cell_dims, map_data, map_data_dims) -> tuple:
        """ Simplified collision detection """
        x, y = round(top_left_pos[0]), round(top_left_pos[1])
        cell_x, cell_y = x // cell_dims[0], y // cell_dims[1]

        # Si le rayon est en dehors des limites de la grille
        if cell_x < 0:
            return (OUT_OF_BOUNDS_COLOR, (0, y))
        if cell_y < 0:
            return (OUT_OF_BOUNDS_COLOR, (x, 0))
        if cell_x >= map_data_dims[0]:
            return (OUT_OF_BOUNDS_COLOR, (SCREEN_DIMS[0] - RAY_DIMS[0], y))
        if cell_y >= map_data_dims[1]:
            return (OUT_OF_BOUNDS_COLOR, (x, SCREEN_DIMS[1] - RAY_DIMS[1]))

        cell = map_data[cell_y][cell_x]

        # Si c'est la sortie
        if cell.nature == 2:
            return EXIT_COLOR, (x, y)

        # Si c'est un passage vide
        if cell.nature == 0:
            return 0, None

        # Si c'est un mur
        return cell.color, (x, y)

    @staticmethod
    def calculate_dst_to_player(x: int, y: int, player) -> int:
        """ Renvoie la distance au joueur calculée avec pythagore """
        ray_width = abs(player.posx - x)
        ray_height = abs(player.posy - y)
        dst_to_player = sqrt(ray_width ** 2 + ray_height ** 2)
        # Éviter les divisions par zéro durant la modélisation 3D
        return dst_to_player if dst_to_player > 1 else 1

    @staticmethod
    def check_top_left_collision(top_left_pos, cell_dims, map_data, map_data_dims):
        """ Simplified collision detection """
        x = round(top_left_pos[0])
        y = round(top_left_pos[1])
        cell_x = x // cell_dims[0]
        cell_y = y // cell_dims[1]

        if cell_x < 0 or cell_y < 0 or cell_x >= map_data_dims[0] or cell_y >= map_data_dims[1]:
            return True

        cell = map_data[cell_y][cell_x]
        if cell.value != 0:
            return True

        return False

    @staticmethod
    def to_normalised_radians(angle):
        angle = angle % (2 * pi)
        if (angle <= 0):
            angle = (2 * pi) + angle

        return angle

    @staticmethod
    def distance_between(x1, y1, x2, y2):
        return math.sqrt((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1))
