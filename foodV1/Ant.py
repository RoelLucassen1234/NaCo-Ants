from math import sin,cos, atan2, radians, degrees ,sqrt
import random
from enum import Enum

from foodV1.PheromoneGrid import PheromoneGrid

from Nest import Nest
from foodV1.Food import Food
from Pheromone import Pheromone, PheromonesTypes
from Task import Tasks
import numpy as np
#
# random.seed(10)


class Ant():
    def __init__(self, max_steering=1, exploration_prob=0.11, ph_decay=2, detection_range=50, position=[100, 100], ph_grid_size=[300,300], global_grid = None):
        self.current_direction = None

        self.position = position

        #movement
        self.acceleration = [0, 0]
        self.velocity = [0, 0]
        self.steering = 1
        self.angle = random.randint(0, 180)
        self.dDir = [cos(radians(self.angle)), sin(radians(self.angle))]
        self.nest = [100, 150]

        #Test
        self.ph_map = (int(ph_grid_size[0]/ 5), int(ph_grid_size[1] / 5))
        self.isMyTrail = PheromoneGrid(ph_grid_size[0], ph_grid_size[1])
        self.global_pheromone_grid = global_grid


        # Genetic Properties
        self.max_steering = max_steering
        self.exploration_prob = exploration_prob
        self.ph_decay = ph_decay
        self.detection_range = detection_range

        self.speed = 0.6
        self.fitness = 0

        self.detected_objects = []

        # Detection

        self.current_task = Tasks.FindFood

        # Time
        self.time_spend = 0

        # Pheromones
        self.limit = 10
        self.ph_max = 0
        self.ph_tick = 16  # Dropping every 10 frames
        # Statistics
        self.p_drop_current = 0
        self.steps_to_home = 0
        self.initial_position = position

    def scan_objects_in_radius(self, objects):
        self.detected_objects = []
        nearby_objects_around_ant = objects.get_objects_nearby(self)

        for obj in nearby_objects_around_ant:
            distance = sqrt((obj.position[0] - self.position[0]) ** 2 + (obj.position[1] - self.position[1]) ** 2)
            # Get Radius around ant and object and check if within eachother

            if distance < self.detection_range:
                self.detected_objects.append(obj)

        return self.detected_objects
    def search_target(self):
        oldest_pheromone_position = None
        oldest_pheromone_age = float('inf')

        for obj in self.detected_objects:
            if self.current_task == Tasks.FindHome and isinstance(obj, Nest):
                return obj.position
            elif self.current_task == Tasks.FindFood and isinstance(obj,Food):
                return obj.position
            elif isinstance(obj, Pheromone):
                if self.current_task == Tasks.FindHome and obj.type == PheromonesTypes.FoundHome:
                    if obj.life < oldest_pheromone_age:
                        oldest_pheromone_age = obj.life
                        oldest_pheromone_position = obj.position
                elif self.current_task == Tasks.FindFood and obj.type == PheromonesTypes.FoundFood:
                    if obj.life < oldest_pheromone_age:
                        oldest_pheromone_age = obj.life
                        oldest_pheromone_position = obj.position
        return oldest_pheromone_position



    def get_steering_force(self, target):
        desired = (target[0] - self.position[0], target[1] - self.position[1])
        steering = (desired[0] - self.velocity[0], desired[1] - self.velocity[1])

        magnitude = sqrt(steering[0] ** 2 + steering[1] ** 2)
        if magnitude > self.max_steering:
            scaled_vector = (steering[0] * self.max_steering / magnitude, steering[1] * self.max_steering / magnitude)
            return scaled_vector
        else:
            return steering

    def calculate_sensor_points(self):
        # Calculate sensor points relative to the ant's position and angle
        mid_sens_offset = (20, 0)
        left_sens_offset = (18, -8)
        right_sens_offset = (18, 8)

        # Calculate sensor points using trigonometry
        mid_sens = (self.position[0] + mid_sens_offset[0] * cos(radians(self.angle)),
                    self.position[1] + mid_sens_offset[1] * sin(radians(self.angle)))

        left_sens = (
            self.position[0] + left_sens_offset[0] * cos(radians(self.angle)) - left_sens_offset[1] * sin(radians(self.angle)),
            self.position[1] + left_sens_offset[0] * sin(radians(self.angle)) + left_sens_offset[1] * cos(radians(self.angle)))

        right_sens = (
            self.position[0] + right_sens_offset[0] * cos(radians(self.angle)) - right_sens_offset[1] * sin(radians(self.angle)),
            self.position[1] + right_sens_offset[0] * sin(radians(self.angle)) + right_sens_offset[1] * cos(radians(self.angle)))

        # Round the sensor points to integers
        mid_sens = (int(mid_sens[0]), int(mid_sens[1]))
        left_sens = (int(left_sens[0]), int(left_sens[1]))
        right_sens = (int(right_sens[0]), int(right_sens[1]))

        return left_sens, mid_sens, right_sens

    def is_within_radius(self, point, sensor_point):
        # Check if the distance between the point and sensor_point is within a small radius
        distance_squared = (point[0] - sensor_point[0]) ** 2 + (point[1] - sensor_point[1]) ** 2
        return distance_squared <= self.detection_range ** 2
    def check_detected_objects(self, objects):
        left_sens, mid_sens, right_sens = self.calculate_sensor_points()
        self.detected_objects = []
        nearby_objects_around_ant = objects.get_objects_nearby(self)
        print(len(nearby_objects_around_ant))

        for obj in nearby_objects_around_ant:
            if isinstance(obj, Pheromone):
                # Check if any sensor point is close enough to the position of the Pheromone
                if self.is_within_radius(obj.position, left_sens) or \
                        self.is_within_radius(obj.position, mid_sens) or \
                        self.is_within_radius(obj.position, right_sens):
                    self.detected_objects.append(obj)
            elif isinstance(obj, Food):
                # Check if any sensor point is close enough to the position of the Food
                if self.is_within_radius(obj.position, left_sens) or \
                        self.is_within_radius(obj.position, mid_sens) or \
                        self.is_within_radius(obj.position, right_sens):
                    self.detected_objects.append(obj)
            elif isinstance(obj, Nest):
                # Check if any sensor point is close enough to the position of the Nest
                if self.is_within_radius(obj.position, left_sens) or \
                        self.is_within_radius(obj.position, mid_sens) or \
                        self.is_within_radius(obj.position, right_sens):
                    self.detected_objects.append(obj)

        return self.detected_objects
    def collision(self, obj):
        distance = sqrt((self.position[0] - obj.position[0]) ** 2 + (self.position[1] - obj.position[1]) ** 2)

        # Calculate the sum of the radii of the ant and the object
        sum_of_radii = obj.width - 2

        # Check if the distance between their centers is less than the sum of their radii
        if distance < sum_of_radii:
            return True  # Collision detected

    def check_collisions(self):

        for obj in self.detected_objects:
            if isinstance(obj, Nest) and self.current_task == Tasks.FindHome:
                if self.collision(obj):
                    self.current_task = Tasks.FindFood
                    self.ph_max = 0
                    self.p_drop_current = 0
                    self.nest = obj.position
                    return True
            elif isinstance(obj, Food) and self.current_task == Tasks.FindFood:
                if self.collision(obj):
                    self.current_task = Tasks.FindHome
                    self.ph_max = 0
                    self.p_drop_current = 0
                    return True

    def move_direction_update(self, boundaries, dt=1):

        target = self.search_target()

        if target:
            target_dir = [target[0] - self.position[0], target[1] - self.position[1]]
            target_dir_mag = sqrt(target_dir[0] ** 2 + target_dir[1] ** 2)
            if target_dir_mag != 0:
                target_dir = [target_dir[0] / target_dir_mag, target_dir[1] / target_dir_mag]

            # Blend the target direction with current direction
            self.dDir[0] += (target_dir[0] - self.dDir[0]) * 0.1  # 0.1 is the blend factor
            self.dDir[1] += (target_dir[1] - self.dDir[1]) * 0.1
        else:
            randAng = random.randint(0, 360)
            randRad = radians(randAng)
            randDir = [cos(randRad), sin(randRad)]

            dDir_x = self.dDir[0] + randDir[0] * self.exploration_prob
            dDir_y = self.dDir[1] + randDir[1] * self.exploration_prob

            dDir_mag = sqrt(dDir_x ** 2 + dDir_y ** 2)
            if dDir_mag != 0:
                self.dDir = [dDir_x / dDir_mag, dDir_y / dDir_mag]

            if self.current_task == Tasks.FindHome:
                # Calculate the vector from ant position to nest
                vector_to_nest = [self.nest[0] - self.position[0], self.nest[1] - self.position[1]]

                # Calculate the magnitude of the vector
                magnitude = sqrt(vector_to_nest[0] ** 2 + vector_to_nest[1] ** 2)

                # Normalize the vector
                normalized_vector = [vector_to_nest[0] / magnitude, vector_to_nest[1] / magnitude]


                # # Add the scaled vector to self.dDir
                # self.dDir[0] += normalized_vector[0]
                # self.dDir[1] += normalized_vector[1]


        dzVel = [self.dDir[0] * self.speed, self.dDir[1] * self.speed]
        dzStrFrc = [(dzVel[0] - self.velocity[0]) * self.max_steering, (dzVel[1] - self.velocity[1]) * self.max_steering]

        dzStrFrc_mag = sqrt(dzStrFrc[0] ** 2 + dzStrFrc[1] ** 2)
        if dzStrFrc_mag <= self.steering:
            accel = dzStrFrc
        else:
            accel = [dzStrFrc[0] / dzStrFrc_mag * self.max_steering, dzStrFrc[1] / dzStrFrc_mag * self.max_steering]

        velo = [self.velocity[0] + accel[0] * dt, self.velocity[1] + accel[1] * dt]

        velo_mag = sqrt(velo[0] ** 2 + velo[1] ** 2)
        if velo_mag <= self.speed:
            self.velocity = velo
        else:
            self.velocity = [velo[0] / velo_mag * self.speed, velo[1] / velo_mag * self.speed]

        # Update position based on the updated velocity, scaled by delta time (dt)
            # Update position based on velocity
        new_pos_x = self.position[0] + self.velocity[0]
        new_pos_y = self.position[1] + self.velocity[1]
        # self.position = [self.position[0] + self.velocity[0] * dt, self.position[1] + self.velocity[1] * dt]

        # Handle boundary wrapping
        # Handle boundary wrapping
        # Check if new position falls within boundaries

        if (boundaries[0][0] <= new_pos_x <= boundaries[1][0]) and (boundaries[0][1] <= new_pos_y <= boundaries[1][1]):
            # If new position is within boundaries, update position
            self.position = [new_pos_x, new_pos_y]
        else:
            # If new position is out of bounds, invert the direction completely
            self.velocity = [-self.velocity[0], -self.velocity[1]]
            self.dDir = [-self.dDir[0], -self.dDir[1]]  # Invert the direction vector as well

        if self.check_collisions():
            # # If new position is out of bounds, invert the direction completely
            # self.velocity = [-self.velocity[0], -self.velocity[1]]
            self.dDir = [-self.dDir[0], -self.dDir[1]]  # Invert the direction vector as well
            self.angle = degrees(atan2(-self.velocity[1], -self.velocity[0]))
        else:
            self.angle = degrees(atan2(self.velocity[1], self.velocity[0]))

        self.acceleration = [0, 0]


    def update_time_spend(self):
        if self.current_task != Tasks.GatherAnts:
            self.time_spend += 1

    def update_position(self, boundaries):

        self.velocity = [self.velocity[0] + self.acceleration[0], self.velocity[1] + self.acceleration[1]]

        speed = sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        if speed > self.speed:
            self.velocity = [self.velocity[0] * self.speed / speed, self.velocity[1] * self.speed / speed]
        elif speed < self.speed:
            self.velocity = [self.velocity[0] * self.speed, self.velocity[1] * self.speed]

        # Normalize velocity to maintain constant speed
        speed = sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        if speed != 0:
            self.velocity = [self.velocity[0] / speed, self.velocity[1] / speed]

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

        # self.check_boundaries(boundaries)

        if self.velocity != [0, 0]:
            self.current_direction = atan2(self.velocity[1], self.velocity[0])

        # # Reset acceleration
        # if self.acceleration != [0,0]:
        #     self.previous_acc = self.acceleration.copy()


    def drop_pheromones(self):
        if self.current_task == Tasks.FindFood:
            if self.ph_tick == self.p_drop_current and self.ph_max < self.limit:
                self.p_drop_current = 0
                self.ph_max += 1
                return Pheromone(self.position, 500, pheromone_type=PheromonesTypes.FoundHome,
                                 pheromone_strength=self.ph_decay)
            else:
                self.p_drop_current += 1

        elif self.current_task == Tasks.FindHome:
            if self.ph_tick == self.p_drop_current and self.ph_max < self.limit:
                self.p_drop_current = 0
                self.ph_max += 1
                return Pheromone(self.position, 1000, pheromone_type=PheromonesTypes.FoundFood,
                                 pheromone_strength=self.ph_decay)
            else:
                self.p_drop_current += 1

    def set_fitness(self, val):
        self.fitness = val
