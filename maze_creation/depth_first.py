from random import randint, choice
from settings import *
from cell import *


class DepthFirst:
    def __init__(self, grid_dims) -> None:

	    # Initialisation d'une grille pleine de murs
        self.map_data = [[Cell(nature=WALL, color=(randint(100, 255), randint(100, 255), randint(100, 255))) for _ in range(grid_dims[0])] for _ in range(grid_dims[1])]

	    # Choix de la cellule de départ (aléatoire)
        self.starting_cell = (randint(0, grid_dims[0] - 1), randint(0, grid_dims[1] - 1))

        self.current_grid_pos = self.starting_cell
        self.grid_dims = (len(self.map_data[0]), len(self.map_data))

        self.stack = [self.starting_cell]
        self.already_visited_cells = [self.starting_cell]
        self.convert_to_ground(self.starting_cell)

        self.current_distance = 0
        self.longest_distance = 0

        self.furthest_pos = None
    
    def is_out_of_bounds(self, cell_grid_pos):
        x = cell_grid_pos[0]
        y = cell_grid_pos[1]
        return not (0 <= x < self.grid_dims[0] and 0 <= y < self.grid_dims[1])
    
    @staticmethod
    def find_middle_cell(first_cell, second_cell):
        middle_x = (first_cell[0] + second_cell[0]) // 2
        middle_y = (first_cell[1] + second_cell[1]) // 2
        return (middle_x, middle_y)
    
    def find_available_neighbours(self):
        neighbours = []

        possible_moves = [(0, -2), (-2, 0), (0, 2), (2, 0)]

        for move in possible_moves:
            neighbour_grid_pos = (self.current_grid_pos[0] + move[0], self.current_grid_pos[1] + move[1])
            if self.is_out_of_bounds(neighbour_grid_pos):
                continue
            if neighbour_grid_pos in self.already_visited_cells:
                continue

            cell = self.map_data[neighbour_grid_pos[1]][neighbour_grid_pos[0]]
            if cell.nature == EMPTY:
                continue
            neighbours.append(neighbour_grid_pos)
        
        return neighbours
    
    def convert_to_ground(self, cell_pos):
        cell = self.map_data[cell_pos[1]][cell_pos[0]]
        cell.nature = EMPTY
    
    def generate_maze(self):
        maze_generating = True
        while maze_generating:

            if not self.stack:
                maze_generating = False
                continue

            # Trouver les voisins disponibles
            neighbours = self.find_available_neighbours()

            # S'il n'y a pas de voisins, faire du backtracking
            if not neighbours and self.stack:
                self.current_grid_pos = self.stack.pop()
                self.current_distance -= 1
                continue

            # Choisir un voisin au hasard et trouver la cellule intermédiaire
            new_cell_grid_pos = choice(neighbours)
            middle_cell = self.find_middle_cell(self.current_grid_pos, new_cell_grid_pos)

            # Transformer ces cellules en sol
            self.convert_to_ground(middle_cell)
            self.convert_to_ground(new_cell_grid_pos)

            # Ajouter la nouvelle cellule au stack et aux cellules déjà visitées
            self.stack.append(new_cell_grid_pos)
            self.already_visited_cells.append(new_cell_grid_pos)

            # La nouvelle cellule devient la cellule actuelle
            self.current_grid_pos = new_cell_grid_pos

            self.current_distance += 1

            if self.current_distance > self.longest_distance:
                self.longest_distance = self.current_distance
                self.furthest_pos = self.current_grid_pos
        
        
