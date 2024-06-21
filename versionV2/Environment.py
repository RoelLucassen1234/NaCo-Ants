import sys
import pygame
from math import pi, sin, cos, atan2, radians, degrees
from Nest import Nest
from Pheromone import Pheromone, PheromonesTypes
from SpatialHashGrid import SpatialHashGrid
from versionV2.Ant import Ant
from versionV2.Food import Food
from Task import Tasks
import random


class Environment:
    """Create the entire environment or a number x of ants will move
    """

    def __init__(self, ant_number, sim_mode, ants=[], nest=None):
        self.width = 1200
        self.height = 800
        self.spatial_hash_grid = SpatialHashGrid(cell_size=200)

        self.initialize_food()
        self.nest = nest
        if sim_mode == "free":
            self.initialize_free_mode(ant_number)
        elif sim_mode == "EXP":
            self.initialize_exp_mode(ants)

        self.boundaries = [(0, 0), (self.width, self.height)]

    def initialize_food(self):
        food_bits = 200
        f_radius = 50
        for i in range(food_bits):
            dist = pow(i / (food_bits - 1.0), 0.5) * f_radius
            angle = 2 * pi * 0.618033 * i
            fx = 200 + dist * cos(angle)
            fy = 200 + dist * sin(angle)
            self.spatial_hash_grid.add_object(Food((fx, fy)))

    def initialize_free_mode(self, ant_number):
        self.ant_number = ant_number
        self.sim_loop = 0

        if self.nest is None:
            self.nest = Nest([self.width / 3, self.height / 2])
        self.food = Food(position=[200, 150])

        self.spatial_hash_grid.add_object(self.nest)
        self.spatial_hash_grid.add_object(self.food)

        self.ants = [Ant(position=[self.nest.position[0], self.nest.position[1]]) for _ in range(self.ant_number)]

    def initialize_exp_mode(self, ants):
        if self.nest is None:
            self.nest = Nest([600, 600])
        self.spatial_hash_grid.add_object(self.nest)
        self.ants = ants

    def return_ants(self):
        return self.ants

    def ant_logic(self):

        # ants doing ant stuff
        for ant in self.ants:
            ant.check_detected_objects(self.spatial_hash_grid)
            ant.move_direction_update(boundaries=self.boundaries)

            p = ant.drop_pheromones()
            if p is not None:
                self.spatial_hash_grid.add_object(p)

    def env_pheromone_logic(self):
        """"Update pheromones and remove them when below a certain margin"""
        objects = self.spatial_hash_grid.get_objects_of_type(Pheromone)

        for obj in objects:
            obj.update_life()
            if obj.current_strength <= 1:
                self.spatial_hash_grid.remove_object(obj)

    def draw_ants(self, screen):
        """"Draw ants on pygame"""
        for ant in self.ants:
            if ant.current_task == Tasks.FindHome:
                pygame.draw.circle(screen, (128, 0, 128), (int(ant.position[0]), int(ant.position[1])), 2)
            else:
                pygame.draw.circle(screen, (255, 0, 0), (int(ant.position[0]), int(ant.position[1])), 2)

    def draw_nest(self, screen):
        """"Draw Nests"""
        objects = self.spatial_hash_grid.get_objects_of_type(Nest)

        for obj in objects:
            pygame.draw.circle(screen, (144, 144, 0), (int(obj.position[0]), int(obj.position[1])), 8)

    def draw_food(self, screen):
        """"Draw Food"""
        objects = self.spatial_hash_grid.get_objects_of_type(Food)

        for obj in objects:
            pygame.draw.circle(screen, (0, 255, 0), (int(obj.position[0]), int(obj.position[1])),  8)

    def draw_pheromones(self, screen):
        """"Draw Pheromones and give them an alpha value based on their current strength"""
        for p in self.spatial_hash_grid.get_objects_of_type(Pheromone):
            alpha = int((255 * p.current_strength) / p.max_life)
            if p.pheromone_type == PheromonesTypes.FoundHome:
                color = pygame.Color(165, 42, 42)
            else:
                color = pygame.Color(0, 0, 255)
            color.a = alpha  # White color with alpha channel

            # Draw the pheromone as a rectangle with adjusted color opacity
            rect = pygame.Rect(int(p.position[0]), int(p.position[1]), p.width, p.height)
            surface = pygame.Surface((rect.width, rect.height))
            surface.set_alpha(alpha)
            surface.fill(color)
            screen.blit(surface, rect)

    def run_simulation(self, amount_of_runs=20000):
        pygame.init()
        self.spatial_hash_grid.add_object(self.nest)
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Ant Walking")
        clock = pygame.time.Clock()

        while amount_of_runs > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill((0, 0, 0))

            self.ant_logic()
            self.env_pheromone_logic()

            self.draw_pheromones(screen)
            self.draw_nest(screen)
            self.draw_food(screen)
            self.draw_ants(screen)
            pygame.display.flip()
            clock.tick(100)
            amount_of_runs -= 1

        food = 0
        for k in self.ants:
            food += k.food_delivered

        return food

    def set_fitness(self, fitness_value):
        self.fitness = fitness_value

    def run_frames(self, amount_of_runs=2000):
        """"Simulate without drawing. TODO fix the slow calculations. Most likely bloat"""
        i = 0

        while i < amount_of_runs:
            self.ant_logic()
            self.env_pheromone_logic()
            i += 1

        food = 0
        for k in self.ants:
            food += k.food_delivered


        return food

#
# env = Environment(50, "free")
# f = env.run_simulation(amount_of_runs=1600)
