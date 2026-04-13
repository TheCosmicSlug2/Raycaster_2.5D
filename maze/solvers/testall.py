from collections import deque
from settings import EMPTY

""" Ne marche que pour des map avec des nature emty ou wall """

class TestAll:
    def __init__(self, map_data, grid_dims, gridpos1, gridpos2) -> None:
        self.map_data = map_data
        self.grid_dims = grid_dims
        self.start = gridpos1
        self.end = gridpos2
        self.path = [self.start]

        self.current_cell = self.start
        self.exit_path = []
    
    
    def is_valid_end(self, gridpos):
        gx, gy = gridpos
        if not (0 <= gx <= 20) or not (0 <= gy <= 20):
            return False
        return self.map_data[gy][gx].nature == EMPTY
    
    def is_valid(self, gridpos):
        return self.map_data[gridpos[1]][gridpos[0]].nature == EMPTY

    def neighbour_gridpos(self, gridpos) -> list[tuple[int, int]]:
        x, y = gridpos
        voisins = []

        if x > 0:
            voisins.append((x - 1, y))
        if x < self.grid_dims[0] - 1:
            voisins.append((x + 1, y))
        if y > 0:
            voisins.append((x, y - 1))
        if y < self.grid_dims[1] - 1:
            voisins.append((x, y + 1))

        return voisins

    def solve_maze(self):

        def hash(gridpos):
            return gridpos[1] * self.grid_dims[0] + gridpos[0]

        end_nei = self.neighbour_gridpos(self.end)
        idx = 0
        # Pour les fantômes bleus et roses
        while not self.is_valid_end(self.end) and idx < len(end_nei):
            self.end = end_nei[idx]
            idx += 1
        
        if not self.is_valid_end(self.end):
            return [self.start]
        q = deque()
        q.append(self.start)
        max_dst = self.grid_dims[0] * self.grid_dims[1]
        dist = {}
        parent = {}
        for i in range(self.grid_dims[1]):
            for j in range(self.grid_dims[0]):
                dist[hash((j, i))] = max_dst
                parent[hash((j, i))] = None
        dist[hash(self.start)] = 0

        while q:
            current = q.popleft()
            if current == self.end:
                break

            for nei in self.neighbour_gridpos(current):
                if not self.is_valid(nei):
                    continue
                new_dist = dist[hash(current)] + 1
                if new_dist >= dist[hash(nei)]:
                    continue
                dist[hash(nei)] = new_dist
                parent[hash(nei)] = current
                q.append(nei)
        if dist[hash(self.end)] == max_dst:
            return [self.start]
        path = []
        cur = self.end
        while cur != None:
            path.append(cur)
            cur = parent[hash(cur)]
        path.reverse()
        self.exit_path = path
        return path


