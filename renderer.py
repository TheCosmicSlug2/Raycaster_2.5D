from turtle import color

import pygame as pg
from entitites import ColorGhost, Gopnik, PacGom
from settings import FPS, const_wall_height, GREEN, BLUE, CYAN, DARK2GRAY,\
    DARKGRAY, EXIT_COLOR, WHITE1, HALF_PLAYER_VISIBLE_SIZE, BLACK, PLAYER_VISBLE_SIZE, SCREEN_DIMS
from math import sin
from physics_engine.physics import *
from utils import blend_colors, are_identical_colors




class Renderer:
    def __init__(self, level_master, audio, state_master, pacman_mode) -> None:
        self.level_master = level_master
        self.SCREEN = pg.display.set_mode(self.level_master.screen_dims)
        self.clock = pg.time.Clock()
        self.fps = FPS
        self.const_wall_height = const_wall_height
        pg.display.set_caption("2.5D Engine")
        self.audio = audio
        self.state_master = state_master

        pg.font.init()
        self.font = pg.font.SysFont('Arial', 30)
        self.pacman_mode = pacman_mode
        self.set_mode(self.pacman_mode)

        self.render_minimap()
        liste = [pg.image.load(f"images/frame{i}.png") for i in range(6)] + \
            [pg.image.load(f"images/ghost{i}.png") for i in range(4)] + \
            [pg.image.load(f"images/pacgom.png")]
        self.textures = {idx: image for idx, image in enumerate(liste)}
        # CMD
        self.tick = 0
        self.MAX_LINES = 30
        self.LINE_HEIGHT = self.level_master.screenh // self.MAX_LINES
        self.cmdcolor = GREEN
        self.cmdfontname = "Consolas"
        self.cmdfont = pg.font.SysFont(self.cmdfontname, self.LINE_HEIGHT)
        self.border_width = 3

    def set_dims(self, dims):
        self.SCREEN = pg.display.set_mode(dims)

    def set_mode(self, pacman_mode):
        self.border_color = (0, 0, 200) if pacman_mode else (255, 255, 255)
        self.render_3D_background(pacman_mode)

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


    def render_3D_background(self, pacman_mode):
        self._3D_background = pg.Surface(self.level_master.screen_dims_Y_enlarged)

        c1, c2, c3, c4 = (BLACK,BLACK, BLACK, BLACK) if pacman_mode else (BLUE, CYAN, DARK2GRAY, DARKGRAY)
            

        up_rect = pg.Rect(0, 0, self.level_master.screenw, self.level_master.screenh)
        self.draw_vertical_gradient(self._3D_background, up_rect, c1, c2) #BLACK, ORANGE)#
        down_rect = pg.Rect(0, self.level_master.screenh, self.level_master.screenw, self.level_master.screenh)
        self.draw_vertical_gradient(self._3D_background, down_rect, c3, c4)

    """ Calculs : """
    def get_xy_screenpos(self, dpos, player_angle) -> tuple[float, float]:
        # get dst beetween player and exit
        dx, dy = dpos
        theta = get_theta_angle((dx, dy), player_angle)
        dst_from_screen_center = sin(theta) * SCREEN_DIMS[0]#/ ratio
        x = self._3D_background.get_width() // 2 + dst_from_screen_center
        y = self._3D_background.get_height() // 2 # - 1/dst # + distance petite, plus hauteur départ grande
        return x, y
    
    def get_xy_dst(self, pos1, pos2, player_angle):
        dpos = get_dpos(pos1, pos2)
        x, y = self.get_xy_screenpos(dpos, player_angle)
        dst = pythagoras(dpos[0], dpos[1])
        return x, y, dst
    

    def get_triangle_points(self, x, y, dst):
        # Draw pointy triangle head
        tick = self.state_master.global_tick
        y -= const_wall_height/4 - sin(tick / 5) * 100 / dst
        rem_y = 100 * (1 + 6/dst)
        triangle_points = [(x, y), (x-(15 - sin(tick / 4) * 15), y-rem_y), (x+(15 - sin(tick / 4) * 15), y-rem_y)]
        triangle_color = (255, 158 + int(40 * sin(tick / 8)), 0)
        return triangle_points, triangle_color


    def render_3D_foreground(self, rays_data, dic, new_to_old, player_pos, player_angle, nb_entities):
        """ Dessine en 3D avec une liste des distances + "couleurs" pour chque distance """

        self._3D_foreground = pg.Surface(self.level_master.screen_dims_Y_enlarged)

        # Mettre l'arrière plan 3d
        self._3D_foreground.blit(self._3D_background, (0, 0))

        # Exit blitted
        if not self.pacman_mode:
            end_pos = self.level_master.end_middle
            x, y, dst = self.get_xy_dst(player_pos, end_pos, player_angle)
            trian_points, trian_col = self.get_triangle_points(x, y, dst)
            pg.draw.polygon(self._3D_foreground, trian_col, trian_points)


        nb_of_rays = len(rays_data) - nb_entities
        ray_width = self.level_master.screenw / nb_of_rays
        
        for idx, ray in enumerate(rays_data):
            ray_idx, ray_data = ray
            if not ray_data:  # ne pas dessiner les rayons qui vont à l'infini
                continue
            
            old_idx = new_to_old[idx]

            if old_idx >= nb_of_rays - 1:
                # 👉 c’est un ennemi → pas de lookup dans dic
                next_ray_idx, next_ray_data = ray_idx, ray_data
            else:
                next_ray_idx, next_ray_data = dic[old_idx]
            
            
            base_color = (ray_data[0][0])

            if ray_idx == "ennemy":
                data, id = ray_data # La liste ne contient qu'une seule valeur
                pos, dst = data
                x, y = self.get_xy_screenpos(get_dpos(player_pos, pos), player_angle)
                texture = self.textures[id]
                width, height = texture.get_size()
                mult = 100/dst
                nwidth = min(width * mult, 1200)
                nheight = min(height * mult, 1000)
                texture = pg.transform.scale(texture, (nwidth, nheight))
                self._3D_foreground.blit(texture, (x - nwidth // 2, y - nheight // 2))
                continue


            for (ray_color1, ray_dst1), (ray_color2, ray_dst2) in zip(ray_data, next_ray_data):

                # Calculer la hauteur à l'écran du murq
                wall_height = self.level_master.normalised_wall_height / ray_dst1
                next_wall_height = self.level_master.normalised_wall_height / ray_dst2

                # Calculer la position et la largeur du rayon en flottant
                ray_x = ray_idx * ray_width
                ray_x_int = int(ray_x)
                next_ray_x_int = int(ray_x + ray_width)

                # Calculer la largeur en pixels
                ray_width_int = next_ray_x_int - ray_x_int
                
                # print(f"color1 : {ray_color1}, color2 : {ray_color2}, {are_identical_colors(ray_color1, ray_color2)}")
                if are_identical_colors(ray_color1, ray_color2):
                    base_color = blend_colors(ray_color1, base_color, 0.2) # + petit -> + opaque
                    base_color = (
                        int(max(0, base_color[0] - ray_dst1 // 3)),
                        int(max(0, base_color[1] - ray_dst1 // 3)),
                        int(max(0, base_color[2] - ray_dst1 // 3))
                    )
                else:
                    base_color = self.border_color

                # Dessiner le mur
                next_ray_x = next_ray_idx * ray_width
                y = self.level_master.screenh - int(wall_height / 2)
                next_y = self.level_master.screenh - int(next_wall_height / 2)
                wall_slice = pg.Rect(ray_x_int, y, ray_width_int, int(wall_height))

                pg.draw.rect(self._3D_foreground, base_color, wall_slice)
                pg.draw.line(self._3D_foreground, self.border_color, (ray_x_int, y), (next_ray_x, next_y), self.border_width)
                pg.draw.line(self._3D_foreground, self.border_color, (ray_x_int, y + int(wall_height)), (next_ray_x, next_y + int(next_wall_height)), self.border_width)
        


    def render_minimap(self):
        self.minimap = pg.Surface(self.level_master.screen_dims)
        bg = BLACK if self.pacman_mode else WHITE1
        wall_color = (0, 0, 255) if self.pacman_mode else None
        self.minimap.fill(bg)

        for idx_row, row in enumerate(self.level_master.map_data):
            for idx_column, cell in enumerate(row):

                if cell.nature == 0:
                    continue
                if cell.nature in (1, 3):
                    rect_color = wall_color if wall_color else cell.color
                if cell.nature == 2: # Sortie
                    rect_color = EXIT_COLOR

                rect = pg.Rect(
                    idx_column * self.level_master.cellw,
                    idx_row * self.level_master.cellh,
                    self.level_master.cellw,
                    self.level_master.cellh
                )
                pg.draw.rect(self.minimap, rect_color, rect)

    def render_minimap_on_screen(self, player, raycaster, entities):

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
            (200, 200, 0),
            (player_center[0], player_center[1]),
            PLAYER_VISBLE_SIZE[1]
        )

        dic = {
            "yellow": (255, 255, 0),
            "red": (255, 0, 0),
            "blue": (40, 255, 255),
            "pink": (255, 105, 180)
        }

        for en in entities:
            size = PLAYER_VISBLE_SIZE[1]
            if isinstance(en, PacGom):
                color = (255,255,0)
                size = size // 2
            if isinstance(en, ColorGhost):
                color = dic[en.color]
            if isinstance(en, Gopnik):
                color = (255, 0, 0)

            pg.draw.circle(
                self.SCREEN,
                color,
                (en.posx, en.posy),
                size
            )



    def render_3D_foreground_on_screen(self, player_moving, y_angle):
        y_offset = -y_angle

        d_offset = sin(self.state_master.global_tick / 2)
        if player_moving:
            y_offset += d_offset * 7
            if d_offset > 0.9 and not self.state_master.step_playing:
                self.audio.play_rdm(steps=True)
                self.state_master.step_playing = True
            else:
                self.state_master.step_playing = False

        self.SCREEN.blit(self._3D_foreground, (0, y_offset))



    def update(self):
        pg.display.flip()
        self.tick += 1
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

