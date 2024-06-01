import random
class Nest:
    """An ant's nest: ants will leave the nest and bring food sources to the nest

    """

    def __init__(self, position):
        """Gives a random position to the object and displays it in a tkinter canvas
        """
        self.width = 8
        self.height = 8
        self.position = position
        self.posx = random.randrange(0, 100)
        self.posy = random.randrange(0, 100)



