import enum


class PheromonesTypes(enum.Enum):
    FoundHome = 1
    FoundFood = 2


class Pheromone:
    def __init__(self, pos, lifetime=300, pheromone_type=PheromonesTypes.FoundHome):
        """The pheromones are placed in the current position of the ant

        """
        self.width = 1
        self.height = 1
        self.position = pos
        self.life = lifetime
        self.max_life = lifetime
        self.type = pheromone_type

        #For Helpers Class
        self.width = 1
        self.height = 1

    def update_life(self, x=5):
        self.life -= x
        return self.life
