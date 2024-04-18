
class Pheromone:
    def __init__(self, ant, type):
        """The pheromones are placed in the current position of the ant

        """
        self.posx = ant.posx
        self.posy = ant.posy
        self.life = 50
        self.type = type


    def update_life(self, x):
        self.life -= x
        return self.life