import enum
import random


class PheromonesTypes(enum.Enum):
    FoundHome = 1
    FoundFood = 2


class Pheromone:
    def __init__(self, pos, lifetime=300, pheromone_type=PheromonesTypes.FoundHome, pheromone_strength=1, a_idx = -1):
        """The pheromones are placed in the current position of the ant

        """
        self.idx = random.randrange(0,10000)
        self.ant_p = a_idx
        self.position = pos
        self.current_strength = lifetime
        self.max_life = lifetime
        self.pheromone_type = pheromone_type
        self.decay_factor = pheromone_strength

        #For Helpers Class
        self.width = 4
        self.height = 4

    def update_life(self, x=5):
        self.current_strength -= self.decay_factor

        if self.current_strength < 0:
            self.current_strength = 0
        return self.current_strength
