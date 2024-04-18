from Ant import Ant
from Nest import Nest
import random


class Environment:
    """Create the entire environment or a number x of ants will move
    """

    def __init__(self, ant_number, sim_mode):
        self.ant_number = ant_number
        self.sim_mode = sim_mode
        self.sim_loop = 0

        self.pheromones = []



        # Initialization of the nest
        self.nest = Nest()

        x = random.Random(0,100)
        y = random.Random(0, 100)

        # Birth of ants - List contains all ants object
        self.ant_data = [Ant(x,y) for i in range(self.ant_number)]


    def move_forever(self):
        while 1:
            self.f_move()


    def update_pheromones(self):

        for pheromone in self.pheromones:
            # Update the life expectancy of the pheromone by 1
            updated_life = pheromone.update_life(1)

            # Check if the updated life expectancy is less than or equal to 0
            if updated_life <= 0:
                # If the life expectancy is 0 or below, remove the pheromone from the list
                self.pheromones.remove(pheromone)



    def f_move(self):
        """Simulates the movements ants
        """
        self.sim_loop += 1

        #Update life expectency of pheromones
        self.update_pheromones()


        # New ants generated if enough food reserves. Algorithm should do that maybe?


        for ant in self.ant_data:

            # Ant energy depletes if simulation mode = reality
            if self.sim_mode == 'reality':
                ant.set_energy(minus=0.01)
                if ant.energy <= 0:
                    ant.remove_from_display()
                    self.ant_data = [an_ant for an_ant in self.ant_data if an_ant is not ant]
                    continue

            # Movement of ants
            if ant.scout_mode:  # if the ant is looking for a food source

                # if the ant leaves the environment, we adapt its movements for which it stays there
                if ant.posx <= 0 or ant.posy <= 0 or ant.posx >= e_w - 1 or ant.posy >= e_h - 1:
                    # FIXME can't choose from an empty index
                    coord = choice(dont_out(ant))
                else:
                    # Movement of an ant is adjusted according to the pheromones present. If there is no pheromone,
                    # there will be no modification on its movement.
                    coord = pheromones_affinity(ant, self.environment)
                    if not coord:
                        coord = move_tab
                    coord = choice(coord)

                ant.posx += coord[0]
                ant.posy += coord[1]
                self.environment.move(ant.display, coord[0], coord[1])

                collision = collide(self.environment, ant)
                if collision == 2:
                    # if there is a collision between a food source and an ant, the scout mode is removed
                    # with each collision between an ant and a food source, its life expectancy decreases by 1
                    self.food.life -= 1
                    self.environment.itemconfig(self.food.display, fill=get_food_colour(self.food.life))
                    if self.sim_mode == 'reality':
                        ant.set_energy(_CONFIG_['ant']['ini_energy'])

                    # If the food source has been consumed, a new food source is replaced
                    if self.food.life < 1:
                        self.food.replace(self.environment)
                        self.environment.itemconfig(self.food.display, fill=get_food_colour(self.food.life))
                    ant.scout_mode = False
                    self.environment.itemconfig(ant.display, fill=_CONFIG_['graphics']['ant']['notscouting_colour'])

                    # the ant puts down its first pheromones when it touches food
                    _ = [pheromones.append(Pheromone(ant, self.environment))
                         for i in range(_CONFIG_['pheromone']['qty_ph_upon_foodfind'])]

                elif collision == 1:  # Collision with nest => Maybe the ant is hungry
                    if self.sim_mode == 'reality':
                        ant.set_energy(plus=self.nest.feed_ant(ant))


            else:  # If the ant found the food source
                # The position of the nest will influence the movements of the ant
                coord = choice(find_nest(ant, self.environment))
                proba = choice([0] * 23 + [1])
                if proba:
                    pheromones.append(Pheromone(ant, self.environment))
                ant.posx += coord[0]
                ant.posy += coord[1]
                self.environment.move(ant.display, coord[0], coord[1])
                # Ant at nest: if there is a collision between a nest and an ant, the ant switches to scout mode
                if collide(self.environment, ant) == 1:
                    ant.scout_mode = True
                    self.environment.itemconfig(ant.display, fill=_CONFIG_['graphics']['ant']['scouting_colour'])

                    # Ants delivers food to the nest
                    self.nest.food_storage += 1

                    # Ant eats energy from the nest
                    if self.sim_mode == 'reality':
                        ant.set_energy(plus=self.nest.feed_ant(ant))

            if len(self.ant_data) <= 100:
                self.environment.update()

        nb_ants_died = nb_ants_before_famine - len(self.ant_data)
        if nb_ants_died > 0:
            print(f'[{self.sim_loop}] {nb_ants_died} ants have died of starvation.')

        if len(self.ant_data) > 100:
            self.environment.update()

        # Refresh status bar
        if len(self.ant_data) > 0:
            avg_energy = sum([an_ant.energy for an_ant in self.ant_data]) / len(self.ant_data)
        else:
            avg_energy = 0
        self.status_vars[0].set(f'Sim loop {self.sim_loop}')
        self.status_vars[1].set(f'Ants: {len(self.ant_data)}')
        self.status_vars[2].set(f'Energy/ant: {avg_energy:.2f}')
        self.status_vars[3].set(f'Food reserve: {self.nest.food_storage:.2f}')
        self.status_vars[4].set(f'Unpicked food: {self.food.life}')
        self.status_vars[5].set(f'Pheromones: {len(pheromones)}')
