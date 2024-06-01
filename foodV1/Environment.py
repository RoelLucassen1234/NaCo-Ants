import sys
import pygame

from Nest import Nest
from Pheromone import Pheromone, PheromonesTypes
from SpatialHashGrid import SpatialHashGrid
from foodV1.Ant import Ant
from foodV1.Food import Food
from Task import Tasks
import random


class Environment:
    """Create the entire environment or a number x of ants will move
    """

    def __init__(self, ant_number, sim_mode, ants=[]):
        self.width = 300
        self.height = 300
        self.spatial_hash_grid = SpatialHashGrid(cell_size=200)


        if sim_mode == "free":
            self.ant_number = ant_number
            self.sim_mode = sim_mode
            self.sim_loop = 0

            # # Birth of ants - List contains all ants object
            # self.ant_data = [Ant(x,y) for i in range(self.ant_number)]

            self.nest = Nest([100, 150])
            self.food = Food(position=[200, 150])

            self.spatial_hash_grid.add_object(self.nest)
            self.spatial_hash_grid.add_object(self.food)

            self.boundaries = [(0, 0), (self.width, self.height)]

            self.ants = [Ant(position=[self.nest.position[0], self.nest.position[1]]) for _ in range(self.ant_number)]

        elif sim_mode == "EXP":
            self.nest = Nest([600, 600])
            self.spatial_hash_grid.add_object(self.nest)
            self.ants = ants
            self.boundaries = [(0, 0), (self.width, self.height)]

    def move_forever(self):
        while 1:
            self.f_move()

    def return_ants(self):
        return self.ants

    def ant_logic(self):

        # ants doing ant stuff
        for ant in self.ants:
            ant.check_detected_objects(self.spatial_hash_grid)
            print(len(ant.detected_objects))
            ant.move_direction_update(boundaries=self.boundaries)
            # ant.update_position(self.boundaries)
            ant.update_time_spend()
            # ant.detect_objects(self.spatial_hash_grid)
            #

            p = ant.drop_pheromones()
            if p is not None:
                self.spatial_hash_grid.add_object(p)
        #
        # for ant in self.ants:
        #     self.spatial_hash_grid.add_object(ant.drop_pheromones())

    def env_pheromone_logic(self):
        objects = self.spatial_hash_grid.get_objects_of_type(Pheromone)

        for obj in objects:
            obj.update_life()
            if obj.life <= 1:
                self.spatial_hash_grid.remove_object(obj)

    def draw_ants(self, screen):

        for ant in self.ants:
            if ant.current_task == Tasks.FindHome:
                pygame.draw.circle(screen, (128, 0, 128), (int(ant.position[0]), int(ant.position[1])), 2)
            else:
                pygame.draw.circle(screen, (255, 0, 0), (int(ant.position[0]), int(ant.position[1])), 2)

                # Draw sensor lines
            # left_sens, mid_sens, right_sens = ant.calculate_sensor_points()
            # pygame.draw.line(screen, (0, 255, 0), ant.position, left_sens, 1)
            # pygame.draw.line(screen, (0, 255, 0), ant.position, mid_sens, 1)
            # pygame.draw.line(screen, (0, 255, 0), ant.position, right_sens, 1)
            for obj in ant.detected_objects:
                pygame.draw.line(screen, (255, 0, 0), (int(ant.position[0]), int(ant.position[1])),
                                 (int(obj.position[0]), int(obj.position[1])), 1)

            # pygame.draw.circle(screen, (0, 0, 255), (int(ant.position[0]), int(ant.position[1])),
            #                    int(ant.detection_range), 1)

    def draw_nest(self, screen):
        objects = self.spatial_hash_grid.get_objects_of_type(Nest)

        for obj in objects:
            pygame.draw.circle(screen, (144, 144, 0), (int(obj.position[0]), int(obj.position[1])), 8)

    def draw_food(self, screen):
        objects = self.spatial_hash_grid.get_objects_of_type(Food)

        for obj in objects:
            pygame.draw.circle(screen, (0, 255, 0), (int(obj.position[0]), int(obj.position[1])),  8)

    def draw_pheromones(self, screen):
        for p in self.spatial_hash_grid.get_objects_of_type(Pheromone):
            alpha = int((255 * p.life) / p.max_life)
            if p.type == PheromonesTypes.FoundHome:
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
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        RED = (255, 0, 0)
        GREEN = (0, 255, 0)
        BLUE = (0, 0, 255)

        pygame.init()
        self.spatial_hash_grid.add_object(self.nest)
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Ant Walking")
        clock = pygame.time.Clock()
        boundaries = [(0, 0), (self.width, self.height)]

        while amount_of_runs > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    self.spatial_hash_grid.add_object(Nest([mx, my]))
                if event.type == pygame.KEYUP:
                    key = pygame.key.name(event.key)

                    # if key == "a":
                    #     mx, my = pygame.mouse.get_pos()
                    #     self.ants.append(Ant(mx, my, current_task=Tasks.GatherAnts,direction=180))
                    # if key == "s":
                    #     mx, my = pygame.mouse.get_pos()
                    #     self.ants.append(Ant(mx, my, current_task=Tasks.FindFood, direction=90))

            screen.fill((0, 0, 0))
            # for obj in spatial_hash_grid.get_all_objects():
            #     pygame.draw.circle(screen, (0, 0, 255), (int(obj.x), int(obj.y)), 1)

            self.ant_logic()
            self.env_pheromone_logic()


            self.draw_pheromones(screen)
            self.draw_nest(screen)
            self.draw_food(screen)
            self.draw_ants(screen)
            pygame.display.flip()
            clock.tick(100)
            amount_of_runs -= 1

    def run_frames(self, amount_of_runs=2000):
        i = 0

        while i < amount_of_runs:
            self.ant_logic()
            self.env_pheromone_logic()
            i += 1

    # def calculate_loss(self, ant, amount_of_runs):
    #     ant_found_home = 0
    #
    #     # Did the ant find the nest
    #     if ant.current_task == Tasks.GatherAnts:
    #         # ant_found_home = 1
    #         # The steps the ant took to get to the nest
    #         steps_to_home = ant.steps_to_home
    #         loss = (amount_of_runs - steps_to_home)
    #     else:
    #         loss = 0
    #
    #     # loss = ants_found_food + (ants_at_food / len(self.ants))
    #     # loss = ants_found_home + ((amount_of_runs - steps_to_home) / amount_of_runs)
    #     # loss = ant_found_home + (amount_of_runs - steps_to_home)
    #     return loss

env = Environment(42, "free")

env.run_simulation()
