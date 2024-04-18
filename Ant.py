from enum import Enum


class Tasks(Enum):
    FindHome = 1
    FindFood = 2


class Ant:
    """The ant object that will search for a food source in an environment.
    With an initial energy of 10, and ant can make 1000 steps before dying.
    """

    def __init__(self, x,y):
        """Birth of an ant in its nest

        """
        self.posx = x
        self.posy = y
        self.velocity = 12
        self.acceleration = 12
        self.task = Tasks.FindHome
        self.has_food = False

    def drop_pheromones(self):
        return NotImplemented


    def scan_radius(self):
        return NotImplemented

    def movement(self):
        return NotImplemented

    def check_collision(self):
        return NotImplemented

    def update_position(self):
        return NotImplemented



    # def remove_from_display(self):
    #     """ Delete the ant from the canvas.
    #     """
    #     self.canvas.delete(self.display)
    # def update_colour(self):
    #     if self.scout_mode:
    #         if self.energy >= 5:
    #             self.canvas.itemconfig(self.display, fill=_CONFIG_['graphics']['ant']['scouting_colour'])
    #         elif self.energy >= 2:
    #             self.canvas.itemconfig(self.display, fill=_CONFIG_['graphics']['ant']['scouting_lowhealth_colour'])
    #         else:
    #             self.canvas.itemconfig(self.display, fill=_CONFIG_['graphics']['ant']['scouting_criticalhealth_colour'])
    #     else:
    #         self.canvas.itemconfig(self.display, fill=_CONFIG_['graphics']['ant']['notscouting_colour'])
