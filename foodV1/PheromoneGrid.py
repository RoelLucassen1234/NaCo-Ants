import numpy as np

class PheromoneGrid:
    def __init__(self, width, height, decay_factor=0.1, shrink_factor=5):
        self.width = width /shrink_factor
        self.height = height / shrink_factor
        self.grid = np.zeros((width, height))
        self.decay_factor = decay_factor  # Add decay factor

    def update(self):
        # Decay all pheromones
        self.grid -= self.decay_factor
        self.grid[self.grid < 0] = 0  # Ensure pheromone values don't go negative

    def deposit_pheromone(self, pos, strength):
        # Deposit pheromone at given position with specified strength
        x, y = pos
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[x, y] += strength

    def get_pheromone_strength(self, pos):
        # Get pheromone strength at given position
        x, y = pos
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x, y]
        return 0

    def is_within_bounds(self, pos):
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height
