import random
class Nest:
    """An ant's nest: ants will leave the nest and bring food sources to the nest

    """

    def __init__(self):
        """Gives a random position to the object and displays it in a tkinter canvas
        """
        self.posx = random.randrange(0, 100)
        self.posy = random.randrange(0, 100)



