import enum


class PheromonesTypes(enum.Enum):
    FoundHome = 1
    FoundFood = 2


class Pheromone:
    def __init__(self, pos, lifetime=100, pheromone_type=PheromonesTypes.FoundHome):
        """The pheromones are placed in the current position of the ant

        """
        self.position = pos
        self.life = lifetime
        self.type = pheromone_type

    def update_life(self, x):
        self.life -= x
        return self.life
