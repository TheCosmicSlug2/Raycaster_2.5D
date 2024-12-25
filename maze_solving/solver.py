from settings import PLAYER_SPEED, FOV_MAX
from math import radians
from physics_engine.physics import Physics

class Solver:
    def __init__(self, player, level_master) -> None:
        self.player = player
        self.level_master = level_master
        self.is_solving = True
        self.physics = Physics()
        
        # Initial player grid position
        player_grid_pos = self.get_player_grid_pos()
        
        # Find the path from the player's initial position
        level_master.solve_maze(player_grid_pos)

        # Initialize indices for the path to the exit
        self.current_idx_in_maze_solving = 0
        self.expected_pos_in_maze_solving = self.level_master.exit_path[self.current_idx_in_maze_solving]

        # Player state for turning and angle
        self.is_turning = False
        self.player.x_angle = 0

        # Deltas for movement
        self.delta_x = 1
        self.delta_y = 0

        # Define turning speed
        self.turning_speed = 5
    
    def two_path_idx_identical(self, idx1, idx2):
        if 0 <= idx1 < len(self.level_master.exit_path) and 0 <= idx2 < len(self.level_master.exit_path):
            return self.level_master.exit_path[idx1] == self.level_master.exit_path[idx2]
        return False


    def get_player_grid_pos(self):
        return (int(self.player.posx // self.level_master.cell_dims[0]), 
                int(self.player.posy // self.level_master.cell_dims[1]))

    def update_location_in_path(self):
        self.current_idx_in_maze_solving += 1
        self.expected_pos_in_maze_solving = self.level_master.exit_path[self.current_idx_in_maze_solving]

    def check_reached_exit(self):
        # Get current grid position of the player
        self.player_grid_pos = self.get_player_grid_pos()

        if self.player_grid_pos != self.expected_pos_in_maze_solving:
            self.update_location_in_path()

        # Check if the player has reached the exit in the path
        next_path_idx = self.current_idx_in_maze_solving + 1
        if next_path_idx > len(self.level_master.exit_path) - 1:
            return True
        
        return False
    
    def update_deltas(self):
        # Get the next grid position from the exit path
        next_path_idx = self.current_idx_in_maze_solving + 1
        next_grid_pos = self.level_master.exit_path[next_path_idx]

        # Calculate deltas
        self.delta_x = next_grid_pos[0] - self.player_grid_pos[0]
        self.delta_y = next_grid_pos[1] - self.player_grid_pos[1]
    
    def normalize_player_angle(self):
        # Normalize player angle to avoid overflow
        self.player.x_angle = (self.player.x_angle // self.turning_speed) * self.turning_speed

    def adjust_player_angle(self):
        
        # Determine target angle based on deltas
        target_angle = self.physics.delta_to_dir[(self.delta_x, self.delta_y)]
        delta_angle = target_angle - self.player.x_angle

        # Adjust player's angle towards the target angle
        if abs(delta_angle) < self.turning_speed:
            self.player.x_angle = target_angle  # Snap to target angle
            self.is_turning = False
        elif delta_angle < 0:
            self.player.x_angle -= self.turning_speed
        else:
            self.player.x_angle += self.turning_speed
    
    def adjust_player_position(self):
        # Center player on the grid
        if self.delta_x != 0:
            self.player.posy = (self.player.posy // self.level_master.cell_dims[1]) * self.level_master.cell_dims[1] + self.level_master.half_cell_dims[1] 
        if self.delta_y != 0:
            self.player.posx = (self.player.posx // self.level_master.cell_dims[0]) * self.level_master.cell_dims[0] + self.level_master.half_cell_dims[0]
        
        self.player.move(self.physics.forward)
        self.is_turning = True
    
    def check_need_turning(self):
        if self.player.x_angle not in (self.physics.dirs):
            return True
        return False

    def update(self):
        if self.check_reached_exit():
            self.is_solving = False
            return
        
        self.update_deltas()
        if self.check_need_turning:
            self.adjust_player_angle()
        self.adjust_player_position()
        
