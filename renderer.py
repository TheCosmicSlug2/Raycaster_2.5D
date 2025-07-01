import pygame as pg
from settings import FPS, const_wall_height, GREEN, BLUE, CYAN, DARK2GRAY,\
    DARKGRAY, EXIT_COLOR, WHITE1, HALF_PLAYER_VISIBLE_SIZE, BLACK, PLAYER_VISBLE_SIZE, SCREEN_DIMS
from math import sin, sqrt, atan2, pi
from os import system


def normalize_angle(angle):
    return (angle + pi) % (2 * pi) - pi


class Renderer:
    def __init__(self, level_master) -> None:
        self.level_master = level_master
        self.SCREEN = pg.display.set_mode(self.level_master.screen_dims)
        self.clock = pg.time.Clock()
        self.fps = FPS
        self.const_wall_height = const_wall_height
        pg.display.set_caption("2.5D Engine")

        pg.font.init()
        self.font = pg.font.SysFont('Arial', 30)

        self.render_minimap()
        self.render_3D_background()

        # CMD

        self.MAX_LINES = 30
        self.LINE_HEIGHT = self.level_master.screenh // self.MAX_LINES
        self.cmdcolor = GREEN
        self.cmdfontname = "Consolas"
        self.cmdfont = pg.font.SysFont(self.cmdfontname, self.LINE_HEIGHT)

    def set_dims(self, dims):
        self.SCREEN = pg.display.set_mode(dims)


    @staticmethod
    def draw_vertical_gradient(surface, rect, color_start, color_end):
        """Dessine un dégradé vertical sur un rectangle."""
        r1, g1, b1 = color_start
        r2, g2, b2 = color_end

        rect_height = rect.height

        for y in range(rect_height):
            ratio = y / rect_height
            r = r1 + (r2 - r1) * ratio
            g = g1 + (g2 - g1) * ratio
            b = b1 + (b2 - b1) * ratio

            pg.draw.line(
                surface,
                (int(r), int(g), int(b)), (rect.x, rect.y + y),
                (rect.x + rect.width, rect.y + y)
            )


    def render_3D_background(self):
        self._3D_background = pg.Surface(self.level_master.screen_dims_Y_enlarged)

        up_rect = pg.Rect(0, 0, self.level_master.screenw, self.level_master.screenh)
        self.draw_vertical_gradient(self._3D_background, up_rect, BLUE, CYAN) #BLACK, ORANGE)#
        down_rect = pg.Rect(0, self.level_master.screenh, self.level_master.screenw, self.level_master.screenh)
        self.draw_vertical_gradient(self._3D_background, down_rect, DARK2GRAY, DARKGRAY)


    def render_3D_foreground(self, rays_data, exit_gridpos, player_pos, player_angle):
        """ Dessine en 3D avec une liste des distances + "couleurs" pour chque distance """

        self._3D_foreground = pg.Surface(self.level_master.screen_dims_Y_enlarged)

        # Mettre l'arrière plan 3d
        self._3D_foreground.blit(self._3D_background, (0, 0))

        # get dst beetween player and exit
        player_angle =  normalize_angle(player_angle)
        pposx, pposy = player_pos
        eposx, eposy = exit_gridpos
        eposx = (eposx + 0.5) * self.level_master.cellw
        eposy = (eposy + 0.5) * self.level_master.cellh
        dx = pposx - eposx
        dy = pposy - eposy
        dst = sqrt((dx / self.level_master.cellw) ** 2 + (dy / self.level_master.cellh) ** 2)
        angle_to_e = normalize_angle(atan2(dy, dx))
        theta = normalize_angle(player_angle - angle_to_e)

        dst_from_screen_center = sin(theta) * SCREEN_DIMS[0]#/ ratio
        x = self._3D_background.get_width() // 2 + dst_from_screen_center
        y = self._3D_background.get_height() // 2


        nb_of_rays = len(rays_data)
        ray_width = self.level_master.screenw / nb_of_rays
        
        for ray_idx, ray_data in enumerate(rays_data):
            if not ray_data:  # ne pas dessiner les rayons qui vont à l'infini
                continue
            
            base_color = (ray_data[0][0])
            
            for ray_color, ray_dst in ray_data:

                # Calculer la hauteur à l'écran du mur
                wall_height = self.level_master.normalised_wall_height / ray_dst

                # Calculer la position et la largeur du rayon en flottant
                ray_x = ray_idx * ray_width
                ray_x_int = int(ray_x)
                next_ray_x_int = int(ray_x + ray_width)

                # Calculer la largeur en pixels
                ray_width_int = next_ray_x_int - ray_x_int


                base_color = blend_colors(ray_color, base_color, 0.5) # + petit -> + opaque
                # base_color = (
                #     int(max(0, ray_color[0] - ray_dst // 4)),
                #     int(max(0, ray_color[1] - ray_dst // 4)),
                #     int(max(0, ray_color[2] - ray_dst // 4))
                # )


                # Dessiner le mur
                wall_slice = pg.Rect(ray_x_int, self.level_master.screenh - int(wall_height / 2), ray_width_int, int(wall_height))

                pg.draw.rect(self._3D_foreground, base_color, wall_slice)
        
        system("cls")
        
        pg.draw.circle(self._3D_foreground, (0, 255, 255), (x, y), 100 / dst)


    def render_minimap(self):
        self.minimap = pg.Surface(self.level_master.screen_dims)
        self.minimap.fill(WHITE1)

        for idx_row, row in enumerate(self.level_master.map_data):
            for idx_column, cell in enumerate(row):

                if cell.nature == 0:
                    continue
                if cell.nature in (1, 3):
                    rect_color = cell.color
                if cell.nature == 2: # Sortie
                    rect_color = EXIT_COLOR

                rect = pg.Rect(
                    idx_column * self.level_master.cellw,
                    idx_row * self.level_master.cellh,
                    self.level_master.cellw,
                    self.level_master.cellh
                )
                pg.draw.rect(self.minimap, rect_color, rect)

    def render_minimap_on_screen(self, player, raycaster):

        # Render les rays
        self.SCREEN.blit(self.minimap, (0, 0))
        player_center = (
            player.posx + HALF_PLAYER_VISIBLE_SIZE[0],
            player.posy + HALF_PLAYER_VISIBLE_SIZE[1]
        )

        for ray_pos in raycaster.rays_final_pos:
            pg.draw.line(
                self.SCREEN,
                (255, 0, 0),
                (player_center[0], player_center[1]),
                (ray_pos[0], ray_pos[1])
            )

        # Render le joueur
        pg.draw.circle(
            self.SCREEN,
            BLACK,
            (player_center[0], player_center[1]),
            PLAYER_VISBLE_SIZE[1]
        )


    def render_3D_foreground_on_screen(self, player_moving, y_angle, tick):
        y_offset = -y_angle

        if player_moving:
            y_offset += sin(tick / 2) * 7

        self.SCREEN.blit(self._3D_foreground, (0, y_offset))


    def update(self):
        pg.display.flip()
        self.clock.tick(self.fps)

    def setcmdfont(self, font):
        try:
            self.cmdfont = pg.font.Font(font, self.LINE_HEIGHT) # Police personnalisée
            self.cmdfontname = font
        except FileNotFoundError:
            self.cmdfont = pg.font.SysFont(font, self.LINE_HEIGHT) # Police système
            self.cmdfontname = font
        except Exception as e:
            print(f"Erreur lors du chargement de la police : {e}")

    def draw_terminal(self, lines, input, scroll_up):
        self.SCREEN.fill(BLACK)
        y = 0
        for line in lines[-(self.MAX_LINES+scroll_up):]:
            line_surface = self.cmdfont.render(line, True, self.cmdcolor)
            self.SCREEN.blit(line_surface, (10, y))
            y += self.LINE_HEIGHT

        # Ajoute l'input
        if (pg.time.get_ticks() // 500) % 2 == 0:
            cursor = "|"
        else:
            cursor = ""
        input_surface = self.cmdfont.render(f" > {input}{cursor}", True, self.cmdcolor)
        self.SCREEN.blit(input_surface, (10, y))
    
    def autofill_command(self, command_str):
        self.input = command_str


def blend_colors(foreground, background, alpha):
    r1, g1, b1 = foreground
    r2, g2, b2 = background

    r = int(r1 * alpha + r2 * (1 - alpha))
    g = int(g1 * alpha + g2 * (1 - alpha))
    b = int(b1 * alpha + b2 * (1 - alpha))

    return (r, g, b)