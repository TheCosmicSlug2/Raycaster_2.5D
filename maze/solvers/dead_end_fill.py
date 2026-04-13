from copy import deepcopy

class DeadEndFill:
    def __init__(self, map_data, grid_dims, starting_grid_pos, ending_grid_pos) -> None:
        self.original_map_data = map_data
        self.map_data = deepcopy(map_data)
        self.grid_dims = grid_dims
        self.starting_grid_pos = starting_grid_pos
        self.ending_grid_pos = ending_grid_pos
        self.has_removed_cells = True
        self.exit_dst = 0


    def is_out_of_bounds(self, cell_grid_pos):
        x, y = cell_grid_pos
        return not (0 <= x < self.grid_dims[0] and 0 <= y < self.grid_dims[1])

    def find_available_neighbours(self, cell_grid_pos):
        """Retourne le nombre de cellules voisines disponibles (valeur 0 = passage)."""
        neighbours = []
        possible_moves = [(0, -1), (-1, 0), (0, 1), (1, 0)]  # Haut, Gauche, Bas, Droite

        for move in possible_moves:
            neighbour_grid_pos = (cell_grid_pos[0] + move[0], cell_grid_pos[1] + move[1])

            if self.is_out_of_bounds(neighbour_grid_pos):
                continue  # On ignore les cellules en dehors des limites

            cell = self.map_data[neighbour_grid_pos[1]][neighbour_grid_pos[0]]

            if cell.nature == 0:  # Passage libre
                neighbours.append(neighbour_grid_pos)

            if neighbour_grid_pos == self.ending_grid_pos: # Si c'est la sortie
                neighbours.append(neighbour_grid_pos)

        return neighbours

    def remove_dead_ends(self):
        """Supprime les impasses du labyrinthe en transformant les cellules à une seule connexion en mur."""
        self.liste_dead_ends = []
        self.has_removed_cells = False  # Réinitialiser le nombre de cellules supprimées
        dead_ends_removed = 0

        for row_idx, row in enumerate(self.map_data):
            for column_idx, cell in enumerate(row):
                current_cell_grid_pos = (column_idx, row_idx)

                # Ignorer les cellules de départ et d'arrivée
                if current_cell_grid_pos == self.starting_grid_pos or current_cell_grid_pos == self.ending_grid_pos:
                    continue

                # Si ce n'est pas un passage
                if cell.nature != 0:
                    continue

                nb_neighbours = len(self.find_available_neighbours(current_cell_grid_pos))

                # Si la cellule est une impasse (un seul voisin libre)
                if nb_neighbours != 1:
                    continue

                cell.nature = 1  # Transformer en mur
                self.liste_dead_ends.append((column_idx, row_idx))
                dead_ends_removed += 1
                self.has_removed_cells = True

        # if dead_ends_removed > 1:
        #     print(f"[algorythms: DeadEndFill] : Solving... (removed {dead_ends_removed} dead ends)")

    def solve_maze(self):
        """Résout le labyrinthe en supprimant les impasses puis reconstruit le chemin."""
        print("solving maze")
        self.exit_path = []

        while self.has_removed_cells:
            self.remove_dead_ends()

        # --- Reconstruction du chemin ---
        current_pos = self.starting_grid_pos
        self.exit_path = [current_pos]
        previous_pos = None  # pour éviter de revenir en arrière
        visited = []
        visited.append(current_pos)

        while current_pos != self.ending_grid_pos:
            neighbours = self.find_available_neighbours(current_pos)

            # garder uniquement les voisins ≠ précédent
            valid_neighbours = [n for n in neighbours if n not in visited]

            # sécurité anti-boucle infinie
            if not valid_neighbours:
                return

            # dans un labyrinthe "nettoyé", il ne doit rester qu'un chemin
            next_pos = valid_neighbours[0]

            self.exit_path.append(next_pos)
            previous_pos = current_pos
            current_pos = next_pos
            visited.append(next_pos)

            self.exit_dst += 1

    def show_map_data(self):
        total_list = []
        for row_idx, row in enumerate(self.map_data):
            new_row = []
            for column_idx, cell in enumerate(row):
                bouyaa = ""

                if cell.nature == 1:
                    bouyaa = "⬛"

                if cell.nature == 0:
                    bouyaa = "⬜"

                if (column_idx, row_idx) == self.starting_grid_pos:
                    bouyaa = "🟥"

                if cell.nature == 2:
                    bouyaa = "🟩"


                new_row.append(bouyaa)

            string = "".join(new_row)
            total_list.append(string)
