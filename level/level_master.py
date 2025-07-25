from random import randint
from maze.solvers.dead_end_fill import DeadEndFill
from maze.solvers.wall_follower import WallFollower
from maze.depth_first import DepthFirst
from level.cell import Cell
from settings import SCREEN_DIMS, const_wall_height, END, EXIT_COLOR, EMPTY, WALL


class LevelMaster:
    def __init__(self, maze_dimensions, solver):
        self.map_data = []
        self.grid_dims = maze_dimensions
        self.update_screen_dims(SCREEN_DIMS)

        self.map_nature = "maze"
        self.gen_map(self.map_nature)

        self.exit_path = []

        self.wall_idx = 0
        self.solve_method = solver
        self.cell_dims: tuple

        # Constante pour normaliser la distance aux murs
        # Ex : si la grille est grande, la distance au prochain mur va être petite,
        # et on divise donc par une toute petite taille de cellule
        # Ex : si la grille est petite, la distance au prochain mur va être grande,
        # et on divise ainsi par une grande taille de cellule
        self.normalised_wall_height = self.cell_dims[0] * const_wall_height

    @property
    def cellw(self):
        return self.cell_dims[0]

    @property
    def cellh(self):
        return self.cell_dims[1]

    @property
    def screenw(self):
        return self.screen_dims[0]

    @property
    def screenh(self):
        return self.screen_dims[1]
    
    @property
    def end_middle(self):
        eposx = (self.end[0] + 0.5) * self.cellw
        eposy = (self.end[1] + 0.5) * self.cellh
        return eposx, eposy
    
    def get_at(self, x, y) -> None | Cell:
        gridx = int(x // self.cellw)
        gridy = int(y // self.cellh)
        if gridx < 0 or gridy < 0:
            return None
        if gridx > self.grid_dims[0] - 1 or gridy > self.grid_dims[1] - 1:
            return None
        return self.map_data[gridy][gridx]

    def set_at(self, gridpos: tuple[int, int], cell: Cell):
        self.map_data[gridpos[1]][gridpos[0]] = cell


    def check_player_reached_exit(self, player_pos):
        gridx = round(player_pos[0] // self.cellw)
        gridy = round(player_pos[1] // self.cellh)
        return (gridx, gridy) == self.end


    def update_screen_dims(self, new_dims):
        self.screen_dims = new_dims
        self.half_screen_dims = (self.screenw // 2, self.screenh // 2)
        self.cell_dims = (self.screenw // self.grid_dims[0], self.screenh // self.grid_dims[1])
        self.half_cell_dims = (self.cellw // 2, self.cellh // 2)

        self.Y_enlargement = self.screenh // 2
        self.screen_dims_Y_enlarged = (self.screenw, self.screenh + self.Y_enlargement * 2)
        self.half_screen_dims_Y_enlarged = (
            self.screen_dims_Y_enlarged[0] // 2,
            self.screen_dims_Y_enlarged[1] // 2
        )

    def update_cell_dims(self):
        self.cell_dims = (self.screenw // self.grid_dims[0], self.screenh // self.grid_dims[1])

    def set_end_nature(self):
        self.set_at(self.end, Cell(nature=END, color=EXIT_COLOR))

    def gen_map(self, nature: str="empty"):
        self.map_nature = nature
        if self.map_nature == "maze":
            self.maze_generator = DepthFirst(grid_dims=self.grid_dims)
            self.maze_generator.generate_maze()
            self.map_data = self.maze_generator.map_data
            self.player_starting_pos = self.maze_generator.furthest_pos
            self.end = self.maze_generator.starting_cell
            self.set_end_nature()
        else:
            self.map_data = [[Cell(nature=EMPTY) for _ in range(self.grid_dims[0])] for _ in range(self.grid_dims[1])]
            self.player_starting_pos = (randint(0, self.grid_dims[0]-1), randint(0, self.grid_dims[1]-1))
            self.end = (randint(0, self.grid_dims[0]-1), randint(0, self.grid_dims[1]-1))
            self.set_end_nature()

    def solve_maze(self, current_player_grid_pos):
        if self.solve_method == "Dead end fill":
            solver = DeadEndFill(
                map_data=self.map_data,
                grid_dims=self.grid_dims,
                starting_grid_pos=current_player_grid_pos,
                ending_grid_pos=self.end
            )
        elif self.solve_method == ("RH-Follower"):
            solver = WallFollower(
                level_master=self,
                side="right",
                starting_pos=current_player_grid_pos,
            )
        elif self.solve_method == ("LH-Follower"):
            solver = WallFollower(
                level_master=self,
                side="left",
                starting_pos=current_player_grid_pos
            )
        else:
            print("No solver found")
            return

        solver.solve_maze()
        self.exit_path = solver.exit_path
