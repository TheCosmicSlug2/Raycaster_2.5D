class WallFollower:
    def __init__(self, level_master, side, starting_pos) -> None:
        self.side = side
        self.level_master = level_master
        self.map_data = level_master.map_data
        self.starting_grid_pos = starting_pos
        self.ending_grid_pos = level_master.end

        self.current_pos = self.starting_grid_pos

        self.grid_dims = level_master.map_data_dims

        self.exit_path = []
        self.side = side
        self.exit_dst = 0

        self.heading = 0        
        # N E S W - just a helpful reminder
        # 0 1 2 3

        self.turn = {"right": -1, "left": 1}[side]

        self.count = 1 # Turning left, -1 for right

        self.completed = False

    def is_wall(self, pos):
        x, y = pos
        cell = self.map_data[y][x]
        return cell.nature == 1
    
    def is_out_of_bounds(self, pos):
        x, y = pos
        return not (0 <= y < self.grid_dims[0] and 0 <= x < self.grid_dims[1])
    
    def find_neighbours(self):

        neighbourgs = []
        # Haut 
        for vector in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nei_cell = (
                self.current_pos[0] + vector[0],
                self.current_pos[1] + vector[1]
            )
            
            if self.is_out_of_bounds(nei_cell) or self.is_wall(nei_cell):
                neighbourgs.append(None)
            else:
                neighbourgs.append(nei_cell)
        
        return neighbourgs

    def solve_maze(self):

        while self.current_pos != self.ending_grid_pos:
            self.exit_path.append(self.current_pos)

            self.exit_dst += 1

            n = self.find_neighbours()

            # A gauche 
            if n[(self.heading - self.turn) % 4] != None:
                self.heading = (self.heading - self.turn) % 4
                self.current_pos = n[self.heading]
                continue

            # Tour droit
            if n[self.heading] != None:
                self.current_pos = n[self.heading]
                continue

            # A droite
            if n[(self.heading + self.turn) % 4] != None:
                self.heading = (self.heading + self.turn) % 4
                self.current_pos = n[self.heading]
                continue

            # Aller en arrière
            if n[(self.heading + 2) % 4] != None:
                self.heading = (self.heading + 2) % 4
                self.current_pos = n[self.heading]
                continue
        
    
