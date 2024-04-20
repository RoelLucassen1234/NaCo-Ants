import random
import sys
import time
from enum import Enum
import math

import numpy as np
import pygame

from Nest import Nest
from Pheromone import Pheromone, PheromonesTypes
from helpers import QuadTreeNode, Rectangle


class Tasks(Enum):
    FindHome = 1
    FindFood = 2


class Ant:
    def __init__(self, x=100, y=100, speed=0.2, steering=5, wandering_strength=30):
        self.x = x
        self.y = y
        self.position = np.zeros(2)
        self.position[0] = x
        self.position[1] = y
        self.speed = speed
        self.steering = steering
        self.wandering_strength = wandering_strength
        self.direction_counter = 0
        self.current_direction = self.random_steering()
        self.max_direction_change = math.pi / 3
        self.sensor_size = 100
        self.sensor_dst = 10
        self.sensor_spacing = 1
        self.antenna_dst = 20
        self.sensors = [pygame.Vector2() for _ in range(3)]
        self.sensor_data = [0.0 for _ in range(3)]
        self.current_task = Tasks.FindHome
        self.found_home = False
        self.detected_objects = []
        self.fov_angle = 60
        self.fov_length = 80
        self.max_speed = 1



        self.acceleration = [0, 0]
        self.velocity = [speed * math.cos(self.current_direction ), speed * math.sin(self.current_direction )]
        self.pheromoneStrenth = 20

    def random_steering(self):
        # Generate a random angle between 0 and 2*pi
        angle = random.uniform(0, 2 * math.pi)
        # Adjust the angle to make the movement less jittery
        angle += random.uniform(-self.steering, self.steering)
        return angle

    def handle_movement(self):
        # Change direction after a certain number of steps based on wandering strength
        if self.wandering_strength == 0:
            return
        if self.direction_counter <= 0:
            # Generate a random change in direction within the limit of 90 degrees
            new_direction = self.random_steering()
            self.interpolate_direction(new_direction)
            self.direction_counter = int(random.expovariate(1 / self.wandering_strength))
        else:
            self.direction_counter -= 1

        # Update the position based on the current direction and speed
        self.position[0] += self.speed * math.cos(self.current_direction)
        self.position[1] += self.speed * math.sin(self.current_direction)

    def interpolate_direction(self, new_direction):
        # Smoothly transition to the new direction using linear interpolation
        alpha = 0.1  # Adjust this value for smoother or faster transitions
        self.current_direction = (1 - alpha) * self.current_direction + alpha * new_direction

    def update_sensors(self):
        # Calculate sensor positions based on current direction
        for i in range(3):
            angle_offset = (i - 1) * self.sensor_spacing
            angle = self.current_direction + angle_offset
            self.sensors[i].x = self.position[0] + self.sensor_dst * math.cos(angle)
            self.sensors[i].y = self.position[1] + self.sensor_dst * math.sin(angle)

    def detect_objects(self, objects):

        start_time = time.time()  # Start measuring time
        detected = self.objects_within_field_of_view(objects)
        self.detected_objects = []
        # Reset sensor data
        for i in range(3):
            self.sensor_data[i] = 0.0


        # Iterate through objects only once
        for obj_pos in detected:
            # Calculate angle between sensor and object
            obj_angle = math.atan2(obj_pos.y - self.y, obj_pos.x - self.x)
            # Wrap object angle to the range [-pi, pi]
            obj_angle = (obj_angle + math.pi) % (2 * math.pi) - math.pi
            # Check if object angle falls within detection range
            for i, sensor_pos in enumerate(self.sensors):

                # Calculate distance between sensor and object
                dist = sensor_pos.distance_to(obj_pos)
                if dist < self.sensor_size:
                    self.detected_objects.append(obj_pos)
                    # Update sensor data based on object proximity
                    self.sensor_data[i] = max(self.sensor_data[i], 1.0 - dist / self.sensor_size)
        end_time = time.time()  # Stop measuring time
        execution_time = end_time - start_time
        print("detect_objects execution time:", execution_time, "seconds")

    def search_for_food(self, steps):
        print(f"Ant's position: ({self.x}, {self.y})")
        return self.handle_movement()

    def get_steering_force(target, current, velocity):
        desired = (target[0] - current[0], target[1] - current[1])
        steering = (desired[0] - velocity[0], desired[1] - velocity[1])
        return (steering[0] * 0.05, steering[1] * 0.05)

    def periodic_direction_update(self, pheromones, stats, boundaries):
        start_time = time.time()  # Start measuring time
        target = None

        # Check if Food in front of Ant
        if self.current_task == Tasks.FindFood:
            for obj in self.detected_objects:
                if isinstance(obj, "FOOD_LOCATION"):
                    target = obj.position
                    break
        # Check if Home in front of ant
        elif self.current_task == Tasks.FindHome:
            for obj in self.detected_objects:
                if isinstance(obj, Nest):
                    target = obj.position
                    break

        # If target is none, then instead look for pheromones
        if target is None:
            if self.current_task == Tasks.FindFood:
                for obj in self.detected_objects:
                    if isinstance(obj, Pheromone):
                        if obj.type == PheromonesTypes.FoundFood:
                            target = obj.position
                        break
            elif self.current_task == Tasks.FindHome:
                for obj in self.detected_objects:
                    if isinstance(obj, Pheromone):
                        if obj.type == PheromonesTypes.FoundHome:
                            target = obj.position
                            break

        # If no target, then the ant has to search into a random direction
        if target is None:
            print("Target is None")
            self.acceleration = [self.speed * math.cos(random.uniform(0, 2 * math.pi)), self.speed * math.sin(random.uniform(0, 2 * math.pi))]
            end_time = time.time()  # Stop measuring time
            execution_time = end_time - start_time
            print("periodic_direction_update execution time:", execution_time, "seconds")
            return

        # Calculate steering force towards target
        steering_force = self.get_steering_force(target, self.position, self.velocity)

        # Apply steering force with random factor
        steering_factor = random.uniform(0.4, 0.7)
        self.acceleration = [self.acceleration[0] + steering_force[0] * steering_factor,
                             self.acceleration[1] + steering_force[1] * steering_factor]

        # Check if new position falls within boundaries
        new_pos_x = self.position[0] + self.acceleration[0]
        new_pos_y = self.position[1] + self.acceleration[1]
        if not (boundaries[0][0] <= new_pos_x <= boundaries[1][0]) or not (
                boundaries[0][1] <= new_pos_y <= boundaries[1][1]):
            # If out of bounds, reverse the direction
            self.acceleration = [-self.acceleration[0], -self.acceleration[1]]

        end_time = time.time()  # Stop measuring time
        execution_time = end_time - start_time
        print("periodic_direction_update execution time:", execution_time, "seconds")

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

        # Reset acceleration
        self.acceleration = [0, 0]

        end_time = time.time()  # Stop measuring time
        execution_time = end_time - start_time
        print("update_position execution time:", execution_time, "seconds")

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
        self.acceleration = [0,0]


        # Update rotation
        dx = self.position[0] - old_pos_x
        dy = self.position[1] - old_pos_y
        rotation_angle = math.atan2(dy, dx) + math.pi / 2.0
        # transform.rotation = Quat((0, 0, math.sin(rotation_angle / 2), math.cos(rotation_angle / 2)))

    def calculate_field_of_view(self):
        angle1 = self.current_direction - math.radians(self.fov_angle)
        angle2 = self.current_direction + math.radians(self.fov_angle)
        fov_point1 = (self.position[0] + self.fov_length * math.cos(angle1), self.position[1] + self.fov_length * math.sin(angle1))
        fov_point2 = (self.position[0] + self.fov_length * math.cos(angle2), self.position[1] + self.fov_length * math.sin(angle2))
        return [self.position, fov_point1, fov_point2]

    def objects_within_field_of_view(self, objects):
        objects_in_range = []

        for obj in objects:
            # Calculate angle between ant's position and object
            obj_angle = math.atan2(obj.y - self.position[1], obj.x - self.position[0])
            # Calculate difference in angles between the ant's direction and object's angle
            angle_diff = abs(obj_angle - self.current_direction)
            # Check if the object is within the field of view angle
            if angle_diff <= math.radians(self.fov_angle ):  # Assuming the field of view angle is 40 degrees
                # Calculate distance between ant and object
                dist = math.sqrt((obj.x - self.position[0]) ** 2 + (obj.y - self.position[1]) ** 2)
                # Check if the object is within the range of the ant's vision
                if dist <= self.fov_length:  # Assuming the maximum range of vision is 100 units
                    objects_in_range.append(obj)

        return objects_in_range


    def drop_pheromones(self):
        if self.current_task == Tasks.FindHome & self.found_home == True:
            return Pheromone(self.position, 100, pheromone_type=PheromonesTypes.FoundFood)
        elif self.current_task == Tasks.FindFood & self.found_home == True:
            return Pheromone(self.position, 100, pheromone_type=PheromonesTypes.FoundHome)





BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ant = Ant()
ant.search_for_food(100)


def main():
    width = 900
    height = 900
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Ant Walking")
    clock = pygame.time.Clock()
    boundaries = [(0, 0), (width, height)]
    quad = QuadTreeNode(Rectangle(0, 0, width, height))

    ants = [Ant() for _ in range(1)]
    objects = [pygame.Vector2(random.randrange(0, width), random.randrange(height)) for _ in range(200)]

    for obj in objects:
        quad.insert(obj)



    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                objects.append(pygame.Vector2(mx,my))

        screen.fill((255, 255, 255))
        for obj in objects:
            pygame.draw.circle(screen, (0, 0, 255), (int(obj.x), int(obj.y)), 2)

        for ant in ants:

            ant.periodic_direction_update(None, None, boundaries)
            ant.update_position(boundaries)
            ant.update_sensors()
            ant.detect_objects(objects)
            fov = ant.calculate_field_of_view()
            pygame.draw.polygon(screen, BLUE, fov, 1)
            pygame.draw.circle(screen, GREEN, (int(ant.position[0]), int(ant.position[1])), 5)

            for obj in ant.detected_objects:
                pygame.draw.line(screen, (255, 0, 0), (int(ant.position[0]), int(ant.position[1])),
                                 (int(obj.x), int(obj.y)), 2)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()