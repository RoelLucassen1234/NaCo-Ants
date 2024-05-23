import random
import sys
import time
from enum import Enum
import math

import numpy as np
import pygame

from Food import Food
# from Environment import Environment
from Nest import Nest
from Pheromone import Pheromone, PheromonesTypes
from helpers import SpatialHashGrid


class Tasks(Enum):
    FindHome = 1
    FindFood = 2
    GatherAnts = 3


class Ant:
    def __init__(self, x=100, y=100, speed=0.1, steering=5, wandering_strength=1, direction=0, exploration=0.5,
                 current_task=Tasks.FindFood):
        self.position = np.zeros(2)
        self.position[0] = x
        self.position[1] = y
        self.speed = speed
        self.steering = steering
        self.wandering_strength = wandering_strength
        self.direction_counter = 0
        if direction == 0:
            self.current_direction = self.random_steering()
        else:
            self.current_direction = direction
        self.max_direction_change = math.pi / 700
        self.sensor_size = 80
        self.sensor_dst = 10
        self.sensor_spacing = 1
        self.antenna_dst = 30
        self.sensors = [pygame.Vector2() for _ in range(3)]
        self.sensor_data = [0.0 for _ in range(3)]

        self.current_task = current_task
        self.found_home = False
        if self.current_task is Tasks.GatherAnts:
            self.found_home = True
        self.detected_objects = []
        self.max_speed = 1
        self.rotation = 0

        self.fitness = 0
        self.exploration = 0.5

        self.width = 1
        self.height = 1

        self.acceleration = [0, 0]
        self.velocity = [speed * math.cos(self.current_direction), speed * math.sin(self.current_direction)]
        self.pheromoneStrenth = 20
        self.steps_to_home = 0


    def random_steering(self):
        # Generate a random angle between 0 and 2*pi
        angle = random.uniform(0, 2 * math.pi)
        # Adjust the angle to make the movement less jittery
        angle += random.uniform(-self.steering, self.steering)
        return angle

    def update_sensor_positions(self):
        for i, sensor_pos in enumerate(self.sensors):
            angle_offset = (i - 1) * self.sensor_spacing
            angle = self.current_direction + angle_offset + self.rotation
            sensor_pos.x = self.position[0] + self.sensor_dst * math.cos(angle)
            sensor_pos.y = self.position[1] + self.sensor_dst * math.sin(angle)

    def detect_collision(self, obj):
        """
        Detect collision with objects at a given position.
        Returns True if collision is detected, False otherwise.
        """
        # Calculate the distance between the centers of the ant and the object
        distance = math.sqrt((self.position[0] - obj.position[0]) ** 2 + (self.position[1] - obj.position[1]) ** 2)

        # Calculate the sum of the radii of the ant and the object
        sum_of_radii = obj.width - 2

        # Check if the distance between their centers is less than the sum of their radii
        if distance < sum_of_radii:
            self.found_home = True
            return True  # Collision detected

    def detect_objects(self, objects):
        self.detected_objects = []

        # Update sensor positions based on ant's direction
        self.update_sensor_positions()

        for sensor_pos in self.sensors:
            nearby_objects = objects.get_objects_nearby(sensor_pos)
            for obj_pos in nearby_objects:
                # Check if object is within sensor's range and field of view
                distance = math.sqrt(
                    (obj_pos.position[0] - sensor_pos.x) ** 2 + (obj_pos.position[1] - sensor_pos.y) ** 2)
                # Check if object is within sensor's range and field of view
                if distance <= self.sensor_size:
                    obj_angle = math.atan2(obj_pos.position[1] - self.position[1],
                                           obj_pos.position[0] - self.position[0])
                    sensor_angle = math.atan2(sensor_pos.y - self.position[1], sensor_pos.x - self.position[0])
                    angle_diff = abs(obj_angle - sensor_angle)
                    angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
                    if abs(angle_diff) < math.pi / 3:  # Field of view angle
                        self.detected_objects.append(obj_pos)

        return self.detected_objects

    def get_steering_force(self, target, current, velocity):
        desired = (target[0] - current[0], target[1] - current[1])
        steering = (desired[0] - velocity[0], desired[1] - velocity[1])
        return steering[0] * 0.03, steering[1] * 0.07

    def k(self, target):
        desired = (target[0] - self.position[0], target[1] - self.position[1])
        steering = (desired[0] - self.velocity[0], desired[1] - self.velocity[1])
        return steering

    def m(self, vector, max_magnitude):
        magnitude = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
        if magnitude > max_magnitude:
            scaled_vector = (vector[0] * max_magnitude / magnitude, vector[1] * max_magnitude / magnitude)
            return scaled_vector
        else:
            return vector

    def periodic_direction_update(self, pheromones, stats, boundaries):
        target = self.detect_target()

        if target is None:
            self.set_random_direction()
            return

        # Calculate the steering force towards the target
        steering_force = self.k(target)

        # Limit the maximum steering force to prevent sharp turns
        max_steering_force = 0.05  # Adjust as needed
        steering_force = self.m(steering_force, max_steering_force)

        # Apply the steering force to acceleration
        self.acceleration = [self.acceleration[0] + steering_force[0],
                             self.acceleration[1] + steering_force[1]]

        # self.calculate_steering_force(target)
        self.check_boundaries(boundaries)
        # self.update_rotation()
        self.update_direction()

    def detect_target(self):
        oldest_pheromone_position = None
        oldest_pheromone_age = float('inf')

        for obj in self.detected_objects:
            if self.current_task == Tasks.FindFood and isinstance(obj, Food):
                return obj.position
            elif self.current_task == Tasks.FindHome and isinstance(obj, Nest):
                return obj.position
            elif isinstance(obj, Pheromone):
                if self.current_task == Tasks.FindFood and obj.type == PheromonesTypes.FoundFood:
                    # print("CHECK")
                    # print(f"ibj.life {obj.life} < {oldest_pheromone_age}")
                    if obj.life < oldest_pheromone_age:
                        oldest_pheromone_age = obj.life
                        oldest_pheromone_position = obj.position

                elif self.current_task == Tasks.FindHome and obj.type == PheromonesTypes.FoundHome:
                    if obj.life < oldest_pheromone_age:
                        oldest_pheromone_age = obj.life
                        oldest_pheromone_position = obj.position
        return oldest_pheromone_position

    def set_random_direction(self):
        # current_direction = math.atan2(self.velocity[1], self.velocity[0])
        random_angle = random.uniform(self.current_direction - math.pi / 2, self.current_direction + math.pi / 2)
        self.acceleration = [self.speed * math.cos(random_angle),
                             self.speed * math.sin(random_angle)]
        # self.update_rotation()

    def calculate_steering_force(self, target):
        steering_force = self.get_steering_force(target, self.position, self.velocity)
        # Introduce a random perturbation to the steering force
        perturbation = random.uniform(-0.05, 0.05)  # Adjust the range of perturbation as needed
        steering_force = (steering_force[0] + perturbation, steering_force[1] + perturbation)

        # Apply the steering force to acceleration with a scaling factor
        steering_factor = random.uniform(0.4, 0.7)
        self.acceleration = [self.acceleration[0] + steering_force[0] * steering_factor,
                             self.acceleration[1] + steering_force[1] * steering_factor]

    def update_direction(self):
        self.current_direction = math.atan2(self.velocity[1], self.velocity[0])

    def check_boundaries(self, boundaries):
        # new_pos_x = self.position[0] + self.acceleration[0]
        # new_pos_y = self.position[1] + self.acceleration[1]
        # if not (boundaries[0][0] <= new_pos_x <= boundaries[1][0]) or not (
        #         boundaries[0][1] <= new_pos_y <= boundaries[1][1]):
        #     self.acceleration = [-self.acceleration[0], -self.acceleration[1]]
        #

        for obj in self.detected_objects:
            if isinstance(obj, Food):
                if self.detect_collision(obj):
                    self.velocity = [-self.velocity[0], -self.velocity[1]]
                    self.current_task = Tasks.GatherAnts

    def update_rotation(self):
        new_direction = math.atan2(self.acceleration[1], self.acceleration[0])
        angle_diff = new_direction - self.current_direction
        if abs(angle_diff) > self.max_direction_change:
            angle_diff = math.copysign(self.max_direction_change, angle_diff)
        self.rotation = angle_diff

    def update_position(self, boundaries):
        start_time = time.time()  # Start measuring time
        # Update velocity based on acceleration
        self.velocity = (self.velocity[0] + self.acceleration[0], self.velocity[1] + self.acceleration[1])

        speed = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        if speed > self.max_speed:
            self.velocity = (self.velocity[0] * self.max_speed / speed, self.velocity[1] * self.max_speed / speed)

        # Update position based on velocity
        new_pos_x = self.position[0] + self.velocity[0]
        new_pos_y = self.position[1] + self.velocity[1]

        # Check if new position falls within boundaries
        if (boundaries[0][0] <= new_pos_x <= boundaries[1][0]) and (boundaries[0][1] <= new_pos_y <= boundaries[1][1]):
            # If new position is within boundaries, update position
            self.position = [new_pos_x, new_pos_y]
        else:
            # If new position is out of bounds, reverse the direction
            self.velocity = [-self.velocity[0], -self.velocity[1]]

        self.check_boundaries(boundaries)

        if self.velocity != (0, 0):
            self.current_direction = math.atan2(self.velocity[1], self.velocity[0])
        # Reset acceleration
        self.acceleration = [0, 0]

        end_time = time.time()  # Stop measuring time
        execution_time = end_time - start_time
        # print("update_position execution time:", execution_time, "seconds")

    def new_position(self, boundaries):

        old_pos_x, old_pos_y = self.position[0], self.position[1]

        if not math.isnan(self.acceleration[0]) and not math.isnan(self.acceleration[1]):
            # Update velocity
            velocity_len = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
            if velocity_len != 0:
                velocity_normalized = (self.velocity[0] / velocity_len, self.velocity[1] / velocity_len)
            else:
                velocity_normalized = self.velocity
            new_velocity_x = velocity_normalized[0] + self.acceleration[0]
            new_velocity_y = velocity_normalized[1] + self.acceleration[1]

        # Reset acceleration
        self.acceleration = [0, 0]

        # Update rotation
        dx = self.position[0] - old_pos_x
        dy = self.position[1] - old_pos_y
        rotation_angle = math.atan2(dy, dx) + math.pi / 2.0
        # transform.rotation = Quat((0, 0, math.sin(rotation_angle / 2), math.cos(rotation_angle / 2)))

    def drop_pheromones(self):
        if self.current_task == Tasks.FindHome and self.found_home == True:
            return Pheromone(self.position, 100, pheromone_type=PheromonesTypes.FoundFood)
        elif self.current_task == Tasks.FindHome and self.found_home == False:
            return Pheromone(self.position, 100, pheromone_type=PheromonesTypes.FoundFood)
        elif self.current_task == Tasks.FindFood and self.found_home == True:
            return Pheromone(self.position, 100, pheromone_type=PheromonesTypes.FoundHome)
        elif self.current_task == Tasks.GatherAnts and self.found_home == True:
            return Pheromone(self.position, 100, pheromone_type=PheromonesTypes.FoundFood, pheromone_strength=1)

    def set_fitness(self, val):
        self.fitness = val

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ant = Ant()


def main():
    # env = Environment(100, "okay")
    # env.run_simulation()
    width = 900
    height = 900
    k = 0
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pheromones = []
    pygame.display.set_caption("Ant Walking")
    clock = pygame.time.Clock()
    boundaries = [(0, 0), (width, height)]
    spatial_hash_grid = SpatialHashGrid(cell_size=200)
    ants = [Ant() for _ in range(100)]
    # objects = [pygame.Vector2(random.randrange(0, width), random.randrange(height)) for _ in range(0)]
    # for obj in objects:
    #     spatial_hash_grid.add_object(obj)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # objects.append(pygame.Vector2(mx, my))
                # spatial_hash_grid.add_object(pygame.Vector2(mx, my))

        screen.fill((0, 0, 0))
        # for obj in objects:
        #     pygame.draw.circle(screen, (0, 0, 255), (int(obj.x), int(obj.y)), 1)

        # reduce potentcy of pheromones
        for pher in pheromones:
            pher.update_life()
            if pher.life <= 0:
                pheromones.remove(pher)

        # ants doing ant stuff
        for ant in ants:
            ant.periodic_direction_update(None, None, boundaries)
            ant.update_position(boundaries)
            ant.detect_objects(spatial_hash_grid)

        if k == 0:
            for ant in ants:
                pheromones.append(ant.drop_pheromones())

        # DRAWING ANTS
        for ant in ants:
            pygame.draw.circle(screen, GREEN, (int(ant.position[0]), int(ant.position[1])), 1)

            for obj in ant.detected_objects:
                pygame.draw.line(screen, (255, 0, 0), (int(ant.position[0]), int(ant.position[1])),
                                 (int(obj.x), int(obj.y)), 1)

        # Drawing Pheromones
        for p in pheromones:
            alpha = int((255 * p.life) / p.max_life)
            color = pygame.Color(165, 42, 42)
            color.a = alpha  # White color with alpha channel

            # Draw the pheromone as a rectangle with adjusted color opacity
            rect = pygame.Rect(int(p.position[0]), int(p.position[1]), p.width, p.height)
            surface = pygame.Surface((rect.width, rect.height))
            surface.set_alpha(alpha)
            surface.fill(color)
            screen.blit(surface, rect)

        pygame.display.flip()
        clock.tick(100)
        k += 1
        if k > 5:
            k = 0

# if __name__ == "__main__":
#     test()
