import math

# Couleurs
BLACK = (0, 0, 0)
DARK2GRAY = (50, 50, 70)
DARKGRAY = (100, 100, 120)
LIGHTGRAY = (200, 200, 200)
WHITE2 = (230, 230, 230)
WHITE1 = (255, 255, 255)

LIGHTRED = (255, 200, 200)
RED = (255, 0, 0)
ORANGE = (255, 128, 0)
LIGHTGREEN = (120, 255, 120)
GREEN = (0, 255, 0)
CYAN = (200, 200, 255)
BLUE = (0, 0, 255)

OUT_OF_BOUNDS_COLOR = RED
EXIT_COLOR = BLACK


# Labyrinthe
solver_name = "dead_end_fill"


# Ecran
DEFAULT_SCREEN_DIMS = (800, 600)
SCREEN_DIMS = DEFAULT_SCREEN_DIMS
HALF_SCREEN_DIMS = (SCREEN_DIMS[0] // 2, SCREEN_DIMS[1] // 2)
Y_ENLARGEMENT = SCREEN_DIMS[1] // 2
SCREEN_DIMS_Y_ENLARGED = (SCREEN_DIMS[0], SCREEN_DIMS[1] + Y_ENLARGEMENT * 2)
HALF_SCREEN_DIMS_Y_ENLARGED = (SCREEN_DIMS_Y_ENLARGED[0] // 2, SCREEN_DIMS_Y_ENLARGED[1] // 2)


# Cellule :
EMPTY = 0
WALL = 1
END = 2


# Commandes :
command_mode = False
command_input = ""


# Joueur :
PLAYER_VISBLE_SIZE = (10, 10)
HALF_PLAYER_VISIBLE_SIZE = (PLAYER_VISBLE_SIZE[0] // 2, PLAYER_VISBLE_SIZE[1] // 2)
player_side_size = 2
PLAYER_SPAWN_TYPE = "random"
PLAYER_DIMS = (player_side_size, player_side_size)
HALF_PLAYER_DIMS = (PLAYER_DIMS[0] // 2, PLAYER_DIMS[1] // 2)
FOV_MAX = 60 * (math.pi / 180)


# Raycaster :
RAY_DIMS = (3, 3)
RAYCASTER_SIZE = 1
RAYCASTER_RES = 1
RAYCASTER_GAP = 1
NB_RAYS = int(SCREEN_DIMS[0] / RAYCASTER_RES)


# Durées
FPS = 30
ticks_to_update_map = FPS // 3
ticks_to_update_mouse = FPS // 3
ticks_to_update_solving = FPS // 3


# Renderer
const_wall_height = 500
