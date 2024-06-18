import math
import random
from enum import Enum

from Nest import Nest
from Pheromone import Pheromone, PheromonesTypes
from Task import Tasks

random.seed(10)
class Ant():

    def __init__(self, max_steering=15, exploration_prob=0.5, ph_decay=2, detection_range=30, position=[100, 100]):
        self.current_direction = None

        self.position = position

        self.acceleration = [0, 0]
        self.velocity = [1, 1]
        self.steering = 0

        # Genetic Properties
        self.max_steering = max_steering
        self.exploration_prob = exploration_prob
        self.ph_decay = ph_decay
        self.detection_range = detection_range

        self.speed = 1
        self.fitness = 0

        self.detected_objects = []

        # Detection

        self.current_task = Tasks.FindHome

        # Time
        self.time_spend = 0

        # Pheromones

        self.ph_tick = 2  # Dropping every 10 frames
        # Statistics
        self.p_drop_current = 0
        self.steps_to_home = 0

        #Randomness:
        # Define deterministic perturbations for exploration

    def scan_objects_in_radius(self, objects):
        self.detected_objects = []
        nearby_objects_around_ant = objects.get_objects_nearby(self)

        for obj in nearby_objects_around_ant:
            distance = math.sqrt((obj.position[0] - self.position[0]) ** 2 + (obj.position[1] - self.position[1]) ** 2)
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
            elif isinstance(obj, Pheromone):
                if self.current_task == Tasks.FindHome and obj.type == PheromonesTypes.FoundHome:
                    if obj.life < oldest_pheromone_age:
                        oldest_pheromone_age = obj.life
                        oldest_pheromone_position = obj.position
        return oldest_pheromone_position

    def search_pheromones(self):
        oldest = float('-inf')
        pos = None
        for obj in self.detected_objects:
            if type(obj) is Pheromone:
                if obj.life < oldest:
                    oldest = obj.life
                    pos = obj.position
        return pos

    def get_steering_force(self, target):
        desired = (target[0] - self.position[0], target[1] - self.position[1])
        steering = (desired[0] - self.velocity[0], desired[1] - self.velocity[1])

        magnitude = math.sqrt(steering[0] ** 2 + steering[1] ** 2)
        if magnitude > self.max_steering:
            scaled_vector = (steering[0] * self.max_steering / magnitude, steering[1] * self.max_steering / magnitude)
            return scaled_vector
        else:
            return steering

    def collision(self, obj):
        distance = math.sqrt((self.position[0] - obj.position[0]) ** 2 + (self.position[1] - obj.position[1]) ** 2)

        # Calculate the sum of the radii of the ant and the object
        sum_of_radii = obj.width - 2

        # Check if the distance between their centers is less than the sum of their radii
        if distance < sum_of_radii:
            return True  # Collision detected

    def check_collisions(self):

        for obj in self.detected_objects:
            if isinstance(obj, Nest):
                if self.collision(obj):
                    self.velocity = [-self.velocity[0], -self.velocity[1]]
                    self.current_task = Tasks.GatherAnts

    def move_direction_update(self):

        target = self.search_target()

        if target is None:
            if self.current_task == Tasks.GatherAnts:
                explore = self.exploration_prob
            elif self.current_task == Tasks.FindHome:
                explore = self.exploration_prob
            else:
                explore = self.exploration_prob
            if random.random() < explore:
                # Explore: Perturb the current direction by roughly 20%
                if self.velocity:  # Check if velocity exists
                    # Calculate the perturbation
                    perturbation = random.uniform(-0.2, 0.2)
                    perturbation2 = random.uniform(-0.2, 0.2)

                    # # Apply the perturbation to both x and y components of the velocity
                    self.acceleration[0] += perturbation
                    self.acceleration[1] += perturbation2

                    self.velocity[0] += self.acceleration[0]
                    self.velocity[1] += self.acceleration[1]
                    self.current_direction = math.atan2(self.velocity[1], self.velocity[0])

            return

        # Make the Boid start steering towards the target. Also makes it that the boid cannot do a sudden 180
        steering_force = self.get_steering_force(target)

        self.acceleration = [self.acceleration[0] + steering_force[0],
                             self.acceleration[1] + steering_force[1]]

        self.check_collisions()

        self.current_direction = math.atan2(self.velocity[1], self.velocity[0])

        if self.current_task != Tasks.GatherAnts:
            self.steps_to_home += 1

    def update_time_spend(self):
        if self.current_task != Tasks.GatherAnts:
            self.time_spend += 1

    def update_position(self, boundaries):

        self.velocity = [self.velocity[0] + self.acceleration[0], self.velocity[1] + self.acceleration[1]]

        speed = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        if speed > self.speed:
            self.velocity = [self.velocity[0] * self.speed / speed, self.velocity[1] * self.speed / speed]
        elif speed < self.speed:
            self.velocity = [self.velocity[0] * self.speed, self.velocity[1] * self.speed]

        # Normalize velocity to maintain constant speed
        speed = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
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
        # print(self.acceleration)
        if self.velocity != [0, 0]:
            self.current_direction = math.atan2(self.velocity[1], self.velocity[0])

        # # Reset acceleration
        # if self.acceleration != [0,0]:
        #     self.previous_acc = self.acceleration.copy()
        self.acceleration = [0, 0]

    def drop_pheromones(self):

        if self.current_task == Tasks.GatherAnts:
            if self.ph_tick == self.p_drop_current:
                self.p_drop_current = 0
                return Pheromone(self.position, 1600, pheromone_type=PheromonesTypes.FoundHome,
                                 pheromone_strength=self.ph_decay)
            else:
                self.p_drop_current += 1

    def set_fitness(self, val):
        self.fitness = val
