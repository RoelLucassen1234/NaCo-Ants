import sys

import pygame

from Ant import Ant
from Nest import Nest
import random

from helpers import SpatialHashGrid


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

        x = random.randrange(400,401)
        y = random.randrange(400, 401)

        # # Birth of ants - List contains all ants object
        # self.ant_data = [Ant(x,y) for i in range(self.ant_number)]

        self.width = 900
        self.height = 900

        self.boundaries = [(0, 0), (self.width, self.height)]

        self.spatial_hash_grid = SpatialHashGrid(cell_size=200)
        self.ants = [Ant(x,y) for _ in range(self.ant_number)]
        objects = [pygame.Vector2(random.randrange(0, self.width), random.randrange(self.height)) for _ in range(0)]
        for obj in objects:
            self.spatial_hash_grid.add_object(obj)


    def move_forever(self):
        while 1:
            self.f_move()



    def ant_logic(self):

        #reduce potentcy of pheromones
        for pher in self.pheromones:
            pher.update_life()
            if pher.life <= 0:
                self.pheromones.remove(pher)

        #ants doing ant stuff
        for ant in self.ants:
            ant.periodic_direction_update(None, None, self.boundaries)
            ant.update_position(self.boundaries)
            ant.detect_objects(self.spatial_hash_grid)

        for ant in self.ants:
            self.pheromones.append(ant.drop_pheromones())

    def draw_ants(self,screen):
        for ant in self.ants:
            pygame.draw.circle(screen, (0, 255, 0), (int(ant.position[0]), int(ant.position[1])), 1)

            for obj in ant.detected_objects:
                pygame.draw.line(screen, (255, 0, 0), (int(ant.position[0]), int(ant.position[1])),
                                 (int(obj.x), int(obj.y)), 1)

    def draw_pheromones(self):
        return

    def run_simulation(self):
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        RED = (255, 0, 0)
        GREEN = (0, 255, 0)
        BLUE = (0, 0, 255)

        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Ant Walking")
        clock = pygame.time.Clock()
        boundaries = [(0, 0), (self.width, self.height)]
        spatial_hash_grid = SpatialHashGrid(cell_size=200)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    spatial_hash_grid.add_object(pygame.Vector2(mx, my))

            screen.fill((0, 0, 0))
            for obj in spatial_hash_grid.get_all_objects():
                pygame.draw.circle(screen, (0, 0, 255), (int(obj.x), int(obj.y)), 1)

            self.ant_logic()
            self.draw_ants(screen)


            pygame.display.flip()
            clock.tick(60)

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
        # self.update_pheromones()
        #
        #
        # # New ants generated if enough food reserves. Algorithm should do that maybe?
        #
        #
        #
        # self.status_vars[0].set(f'Sim loop {self.sim_loop}')
        # self.status_vars[1].set(f'Ants: {len(self.ant_data)}')
        # self.status_vars[2].set(f'Energy/ant: {avg_energy:.2f}')
        # self.status_vars[3].set(f'Food reserve: {self.nest.food_storage:.2f}')
        # self.status_vars[4].set(f'Unpicked food: {self.food.life}')
        # self.status_vars[5].set(f'Pheromones: {len(pheromones)}')
