from math import sqrt, pi, tan, cos
from physics_engine.physics import Physics
from settings import RAYCASTER_RES, RAYCASTER_GAP, HALF_PLAYER_DIMS,\
    NB_RAYS, EMPTY, OUT_OF_BOUNDS_COLOR

class Raycaster:
    def __init__(self, player, level_master, renderer):
        self.resolution = RAYCASTER_RES
        self.gap = RAYCASTER_GAP
        self.physics = Physics()
        self.player = player
        self.level_master = level_master
        self.renderer = renderer
        self.nb_of_raycasts = 0
        self.max_raycast_distance = sqrt(self.level_master.cellw + self.level_master.cellh) * 10

        self.rays_final_pos = []
        self.raycast_distances = []
        self.raycast_colors = []

    def is_out_of_bounds(self, posx, posy):

        if posx <= 0 or posy <= 0:
            return True
        if posx >= self.level_master.screenw or posy >= self.level_master.screenh:
            return True

        return False

    def has_wall_at(self, x, y) -> bool:
        if self.is_out_of_bounds(x, y):
            return True  # Out of bounds is treated as a wall for edge boundaries

        # Handle the edge case where no wall is detected on top/left
        grid_x = int(x // self.level_master.cellw)
        grid_y = int(y // self.level_master.cellh)

        if grid_x >= self.level_master.grid_dims[0] or grid_y >= self.level_master.grid_dims[1]:
            return True

        return self.level_master.map_data[grid_y][grid_x].nature != EMPTY


    def find_wall_color(self, x, y):
        if self.is_out_of_bounds(x, y):
            return OUT_OF_BOUNDS_COLOR

        gridy = int(y // self.level_master.cellh)
        gridx = int(x // self.level_master.cellw)
        color = self.level_master.map_data[gridy][gridx].color
        return color


    def cast_ray(self, start_pos, angle, map_shown):
        # Normaliser l'angle pour qu'il soit compris entre 0 et 2 * PI
        angle = self.physics.to_normalised_radians(angle)


        # Déterminer les directions (haut/bas/gauche/droite) en fonction de l'angle
        is_facing_down = 0 < angle < pi
        is_facing_up = not is_facing_down
        is_facing_right = angle < 0.5 * pi or angle > 1.5 * pi
        is_facing_left = not is_facing_right

        wall_hit_x = 0
        wall_hit_y = 0

        # HORIZONTAL CHECKING
        found_horizontal_wall = False
        horizontal_hit_x = 0
        horizontal_hit_y = 0

        first_intersection_x = None
        first_intersection_y = None

        if is_facing_up:
            first_intersection_y = (
                start_pos[1] // self.level_master.cellh
                ) * self.level_master.cellh - 0.01
        if is_facing_down:
            first_intersection_y = (
                start_pos[1] // self.level_master.cellh
                ) * self.level_master.cellh + self.level_master.cellh

        # Calcul de x pour cette première intersection en utilisant l'angle
        first_intersection_x = start_pos[0] + (first_intersection_y - start_pos[1]) / tan(angle)


        next_horizontal_x = first_intersection_x
        next_horizontal_y = first_intersection_y

        xa = 0
        ya = 0

        if is_facing_up:
            ya = -self.level_master.cellh
        if is_facing_down:
            ya = self.level_master.cellh

        xa = ya / tan(angle)

        # Boucle pour trouver l'intersection horizontale avec un mur

        # La valeur -1 est choisie car lorsque le rayon n'atteindra jamais le bord haut ou
        # gauche de l'écran sinon.
        # Ce qui conduira à un mur non trouvé et donc à un mauvais dessin du bord
        found_horizontal_wall = False
        while -1 <= next_horizontal_x <= self.level_master.screenw and \
            -1 <= next_horizontal_y <= self.level_master.screenh:
            if self.has_wall_at(next_horizontal_x, next_horizontal_y):
                found_horizontal_wall = True
                horizontal_hit_x = next_horizontal_x
                horizontal_hit_y = next_horizontal_y
                break
            next_horizontal_x += xa
            next_horizontal_y += ya

        wall_hit_x = horizontal_hit_x
        wall_hit_y = horizontal_hit_y

        found_vertical_wall = False
        vertical_hit_x = 0
        vertical_hit_y = 0

        if is_facing_right:
            first_intersection_x = (
                (start_pos[0] // self.level_master.cellw) * self.level_master.cellw
            ) + self.level_master.cellw
        elif is_facing_left:
            first_intersection_x = (
                (start_pos[0] // self.level_master.cellw) * self.level_master.cellw
            ) - 0.01 # L'erreur venait d'ici :3

        first_intersection_y = start_pos[1] + (first_intersection_x - start_pos[0]) * tan(angle)

        next_vertical_x = first_intersection_x
        next_vertical_y = first_intersection_y

        if is_facing_right:
            xa = self.level_master.cellw
        if is_facing_left:
            xa = -self.level_master.cellw

        ya = xa * tan(angle)

        while -1 <= next_vertical_x <= self.level_master.screenw and \
            -1 <= next_vertical_y <= self.level_master.screenh:

            if self.has_wall_at(next_vertical_x, next_vertical_y):
                found_vertical_wall = True
                vertical_hit_x = next_vertical_x
                vertical_hit_y = next_vertical_y
                break
            next_vertical_x += xa
            next_vertical_y += ya

        # Distance calculation

        horizontal_distance = 0
        vertical_distance = 0

        if found_horizontal_wall:
            horizontal_distance = self.physics.distance_between(
                start_pos[0], start_pos[1], horizontal_hit_x, horizontal_hit_y
            )
        else:
            horizontal_distance = 999

        if found_vertical_wall:
            vertical_distance = self.physics.distance_between(
                start_pos[0], start_pos[1], vertical_hit_x, vertical_hit_y
            )
        else:
            vertical_distance = 999

        if horizontal_distance < vertical_distance:
            wall_hit_x = horizontal_hit_x
            wall_hit_y = horizontal_hit_y
        else:
            wall_hit_x = vertical_hit_x
            wall_hit_y = vertical_hit_y

        if map_shown:
            self.rays_final_pos.append((wall_hit_x, wall_hit_y))

        distance = min(horizontal_distance, vertical_distance)
        color = self.find_wall_color(wall_hit_x, wall_hit_y)

        angle_correction = abs(angle - self.player.x_angle)

        distance *= cos(angle_correction)

        return color, distance


    def raycast(self, map_shown: bool) -> tuple:
        self.raycast_distances = []
        self.raycast_colors = []
        self.rays_final_pos = []
        rayAngle = self.player.x_angle - (self.player.fov / 2)
        player_center = (
            self.player.posx + HALF_PLAYER_DIMS[0],
            self.player.posy + HALF_PLAYER_DIMS[1]
        )

        for _ in range(NB_RAYS):

            color, distance = self.cast_ray(player_center, rayAngle, map_shown)
            self.raycast_colors.append(color)
            self.raycast_distances.append(distance)
            rayAngle += self.player.fov / NB_RAYS


    def first_wall_dir(self):
        """ Envoie un ray depuis la direction du joueur jusqu'à un mur """
        posx, posy = self.player.posx, self.player.posy
        lg_x, lg_y = self.physics.trouver_longueurs_trigo(self.player.x_angle)

        while not self.is_out_of_bounds(posx, posy):
            if self.has_wall_at(posx, posy):
                break
            posx += lg_x
            posy += lg_y

        if self.is_out_of_bounds(posx, posy):
            return None

        wall_grid_pos = (int(posx // self.level_master.cellw), int(posy // self.level_master.cellh))
        if wall_grid_pos == self.player.gridpos:
            wall_grid_pos = None

        return wall_grid_pos


    def empty_space_before_wall(self):
        """
        Envoie un ray depuis la direction du joueur jusqu'à
        l'espace situé avant le mur devant le joueur
        """
        posx, posy = self.player.posx, self.player.posy
        lg_x, lg_y = self.physics.trouver_longueurs_trigo(self.player.x_angle)

        while not self.is_out_of_bounds(posx, posy):
            if self.has_wall_at(posx, posy):
                break
            posx += lg_x
            posy += lg_y

        posx -= lg_x
        posy -= lg_y

        wall_grid_pos = (int(posx // self.level_master.cellw), int(posy // self.level_master.cellh))
        if wall_grid_pos == self.player.gridpos:
            wall_grid_pos = None

        return wall_grid_pos

    def every_cell_in_dir(self):
        """
        Envoie un ray depuis la direction du joueur jusqu'à
        l'espace situé avant le mur devant le joueur
        """
        posx, posy = self.player.posx, self.player.posy
        player_grid_pos = self.player.gripos
        lg_x, lg_y = self.physics.trouver_longueurs_trigo(self.player.x_angle)

        wall_pos = []

        while not self.is_out_of_bounds(posx, posy):

            wall_grid_pos = (
                int(posx // self.level_master.cellw),
                int(posy // self.level_master.cellh)
            )
            if wall_grid_pos not in wall_pos and wall_grid_pos != player_grid_pos:
                wall_pos.append(wall_grid_pos)

            posx += lg_x
            posy += lg_y

        return wall_pos



    def every_wall_in_player_direction(self):
        """ Envoie un ray et retourne tous les murs qu'il a croisé """
        liste_murs = []

        posx, posy = self.player.posx, self.player.posy

        top_left_pos = (posx, posy)
        bottom_right_pos = (posx + self.player.width, posy + self.player.height)

        x_grid_positions = (
            top_left_pos[0] // self.level_master.cellw,
            bottom_right_pos[0] // self.level_master.cellw
        )
        y_grid_pos = (
            top_left_pos[1] // self.level_master.cellh,
            bottom_right_pos[1] // self.level_master.cellh
        )

        lg_x, lg_y = self.physics.trouver_longueurs_trigo(self.player.x_angle)


        while 0 < posx < self.level_master.screenw and 0 < posy < self.level_master.screenh:

            # calculer les coordonnées sur la grille
            row = int(posy // self.level_master.cellh)
            column = int(posx // self.level_master.cellw)

            if column in x_grid_positions and row in y_grid_pos:
                posx += lg_x
                posy += lg_y
                continue

            if (row, column) not in liste_murs: # Si le mur n'a pas déjà été ajouté à la liste
                liste_murs.append((row, column))

            posx += lg_x
            posy += lg_y

        return liste_murs
