import math
from enum import Enum
import time
import random

import pygame

from Nest import Nest
from Pheromone import Pheromone, PheromonesTypes


class Tasks(Enum):
    FindHome = 1
    FindFood = 2


class Ant:
    def __init__(self, x=100, y=100, speed=0.1, steering=5, wandering_strength=1):
        self.x = x
        self.y = y
        self.position = [0,0]
        self.position[0] = x
        self.position[1] = y
        self.speed = speed
        self.steering = steering
        self.wandering_strength = wandering_strength
        self.direction_counter = 0
        self.current_direction = self.random_steering()
        self.max_direction_change = math.pi / 360
        self.sensor_size = 60
        self.sensor_dst = 10
        self.sensor_spacing = 1
        self.antenna_dst = 20
        self.sensors = [pygame.Vector2() for _ in range(3)]
        self.sensor_data = [0.0 for _ in range(3)]
        self.current_task = Tasks.FindHome
        self.found_home = False
        self.detected_objects = []
        self.max_speed = 1
        self.rotation = 0

        self.acceleration = [0, 0]
        self.velocity = [speed * math.cos(self.current_direction), speed * math.sin(self.current_direction)]
        self.pheromoneStrenth = 20

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

    def detect_objects(self, objects):
        self.detected_objects = []

        # Update sensor positions based on ant's direction
        self.update_sensor_positions()

        for sensor_pos in self.sensors:
            nearby_objects = objects.get_objects_nearby(sensor_pos)
            for obj_pos in nearby_objects:
                # Check if object is within sensor's range and field of view
                if obj_pos.distance_to(sensor_pos) <= self.sensor_size:
                    obj_angle = math.atan2(obj_pos.y - self.position[1], obj_pos.x - self.position[0])
                    sensor_angle = math.atan2(sensor_pos.y - self.position[1], sensor_pos.x - self.position[0])
                    angle_diff = abs(obj_angle - sensor_angle)
                    angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
                    if abs(angle_diff) < math.pi / 3:  # Field of view angle
                        self.detected_objects.append(obj_pos)

        return self.detected_objects

    def get_steering_force(target, current, velocity):
        desired = (target[0] - current[0], target[1] - current[1])
        steering = (desired[0] - velocity[0], desired[1] - velocity[1])
        return steering[0] * 0.03, steering[1] * 0.03

    def periodic_direction_update(self, pheromones, stats, boundaries):
        target = self.detect_target()

        if target is None:
            self.set_random_direction()
            return

        self.calculate_steering_force(target)
        self.update_direction()
        self.check_boundaries(boundaries)

    def detect_target(self):
        for obj in self.detected_objects:
            if self.current_task == Tasks.FindFood and isinstance(obj, "FOOD_LOCATION"):
                return obj.position
            elif self.current_task == Tasks.FindHome and isinstance(obj, Nest):
                return obj.position
            elif isinstance(obj, Pheromone):
                if self.current_task == Tasks.FindFood and obj.type == PheromonesTypes.FoundFood:
                    return obj.position
                elif self.current_task == Tasks.FindHome and obj.type == PheromonesTypes.FoundHome:
                    return obj.position
        return None

    def set_random_direction(self):
        # current_direction = math.atan2(self.velocity[1], self.velocity[0])
        random_angle = random.uniform(self.current_direction - math.pi / 2, self.current_direction + math.pi / 2)
        self.acceleration = [self.speed * math.cos(random_angle),
                             self.speed * math.sin(random_angle)]
        self.update_rotation()

    def calculate_steering_force(self, target):
        steering_force = self.get_steering_force(target, self.position, self.velocity)
        steering_factor = random.uniform(0.4, 0.7)
        self.acceleration = [self.acceleration[0] + steering_force[0] * steering_factor,
                             self.acceleration[1] + steering_force[1] * steering_factor]
        self.update_rotation()

    def update_direction(self):
        self.current_direction = math.atan2(self.velocity[1], self.velocity[0])

    def check_boundaries(self, boundaries):
        new_pos_x = self.position[0] + self.acceleration[0]
        new_pos_y = self.position[1] + self.acceleration[1]
        if not (boundaries[0][0] <= new_pos_x <= boundaries[1][0]) or not (
                boundaries[0][1] <= new_pos_y <= boundaries[1][1]):
            self.acceleration = [-self.acceleration[0], -self.acceleration[1]]

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
        elif self.current_task == Tasks.FindFood and self.found_home == True:
            return Pheromone(self.position, 100, pheromone_type=PheromonesTypes.FoundHome)