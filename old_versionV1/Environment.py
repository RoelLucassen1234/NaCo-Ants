import sys
import pygame

from Nest import Nest
from Pheromone import Pheromone
from SpatialHashGrid import SpatialHashGrid
from old_versionV1.Ant import Ant
from Task import Tasks


class Environment:
    """Create the entire environment or a number x of ants will move
    """

    def __init__(self, ant_number, sim_mode, ants=[]):
        self.width = 900
        self.height = 900
        self.spatial_hash_grid = SpatialHashGrid(cell_size=200)

        if sim_mode == "free":
            self.ant_number = ant_number
            self.sim_mode = sim_mode
            self.sim_loop = 0

            self.nest = Nest([600, 600])
            self.spatial_hash_grid.add_object(self.nest)

            self.boundaries = [(0, 0), (self.width, self.height)]

            self.spatial_hash_grid = SpatialHashGrid(cell_size=200)
            self.ants = [Ant(position=[self.nest.position[0], self.nest.position[1]]) for _ in range(self.ant_number)]

        elif sim_mode == "EXP":
            self.nest = Nest([600, 600])
            self.spatial_hash_grid.add_object(self.nest)
            self.ants = ants
            self.boundaries = [(0, 0), (self.width, self.height)]

    def return_ants(self):
        return self.ants

    def ant_logic(self):

        # ants doing ant stuff
        for ant in self.ants:
            ant.scan_objects_in_radius(self.spatial_hash_grid)
            ant.move_direction_update()
            ant.update_position(self.boundaries)
            p = ant.drop_pheromones()

            if p is not None:
                self.spatial_hash_grid.add_object(p)

    def env_pheromone_logic(self):
        objects = self.spatial_hash_grid.get_objects_of_type(Pheromone)

        for obj in objects:
            obj.update_life()
            if obj.current_strength <= 1:
                self.spatial_hash_grid.remove_object(obj)

    def draw_ants(self, screen):

        for ant in self.ants:
            if ant.current_task == Tasks.FindHome:
                pygame.draw.circle(screen, (0, 255, 0), (int(ant.position[0]), int(ant.position[1])), 1)
            else:
                pygame.draw.circle(screen, (255, 0, 0), (int(ant.position[0]), int(ant.position[1])), 1)

            # for obj in ant.detected_objects:
            #     pygame.draw.line(screen, (255, 0, 0), (int(ant.position[0]), int(ant.position[1])),
            #                      (int(obj.position[0]), int(obj.position[1])), 1)

            pygame.draw.circle(screen, (0, 0, 255), (int(ant.position[0]), int(ant.position[1])),
                               int(ant.detection_range), 1)

    def draw_nest(self, screen):
        objects = self.spatial_hash_grid.get_objects_of_type(Nest)
        print(len(objects))
        for obj in objects:
            pygame.draw.circle(screen, (144, 144, 0), (int(obj.position[0]), int(obj.position[1])), 4)

    def draw_pheromones(self, screen):
        for p in self.spatial_hash_grid.get_objects_of_type(Pheromone):
            alpha = int((255 * p.current_strength) / p.max_life)
            color = pygame.Color(165, 42, 42)
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
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Ant Walking")
        clock = pygame.time.Clock()
        boundaries = [(0, 0), (self.width, self.height)]

        # spatial_hash_grid = SpatialHashGrid(cell_size=200)

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

            self.draw_ants(screen)
            self.draw_pheromones(screen)
            self.draw_nest(screen)
            pygame.display.flip()
            clock.tick(100)
            amount_of_runs -= 1

    def run_frames(self, amount_of_runs=2000):
        i = 0

        while i < amount_of_runs:
            self.ant_logic()
            self.env_pheromone_logic()
            i += 1

#
# env = Environment(50, "free")
#
# env.run_simulation()
