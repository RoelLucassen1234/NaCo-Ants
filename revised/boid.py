import math
import random

from Food import Food
from Nest import Nest
from Pheromone import Pheromone, PheromonesTypes
from Tests import Tasks


class Boid():

    def __init__(self):
        self.current_direction = None
        self.position = [100, 100]
        self.acceleration = [1, 1]
        self.velocity = [1, 1]

        self.speed = 1
        self.fitness = 0

        self.detected_objects = []

        # Detection
        self.detection_range = 60
        self.current_task = Tasks.FindFood

        # Exploration
        self.exploration_prob = 0.01

        #Time
        self.time_spend = 0

        #Pheromones
        self.p_drop = True

    def scan_objects_in_radius(self, objects):
        self.detected_objects = []
        nearby_objects_around_ant = objects.get_objects_nearby(self)


        for obj in nearby_objects_around_ant:
            distance = math.sqrt((obj.position[0] - self.position[0]) ** 2 + (obj.position[1] - self.position[1]) ** 2)
            # Get Radius around ant and object and check if within eachother

            if distance <= self.detection_range:
                self.detected_objects.append(obj)

        return self.detected_objects

    def search_target(self):
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

    def get_steering_force(self, target):
        desired = (target[0] - self.position[0], target[1] - self.position[1])
        steering = (desired[0] - self.velocity[0], desired[1] - self.velocity[1])
        max_steering_force = 0.10  # Adjust as needed

        magnitude = math.sqrt(steering[0] ** 2 + steering[1] ** 2)
        if magnitude > max_steering_force:
            scaled_vector = (steering[0] * max_steering_force / magnitude, steering[1] * max_steering_force / magnitude)
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
            if isinstance(obj, Food):
                if self.collision(obj):
                    self.velocity = [-self.velocity[0], -self.velocity[1]]
                    self.current_task = Tasks.GatherAnts

    def move_direction_update(self):
        target = self.search_target()

        if target is None:
            if random.random() < self.exploration_prob:
                # Explore: Perturb the current direction by roughly 20%
                if self.velocity:  # Check if velocity exists
                    # Calculate the perturbation
                    perturbation = random.uniform(-0.2, 0.2)
                    perturbation2 = random.uniform(-0.2, 0.2)

                    # Apply the perturbation to both x and y components of the velocity
                    self.acceleration[0] += perturbation
                    self.acceleration[1] += perturbation2

                    # self.velocity[0] += self.acceleration[0]
                    # self.velocity[1] += self.acceleration[1]
                    # self.current_direction = math.atan2(self.velocity[1], self.velocity[0])


            return

        # Make the Boid start steering towards the target. Also makes it that the boid cannot do a sudden 180
        steering_force = self.get_steering_force(target)

        self.acceleration = [self.acceleration[0] + steering_force[0],
                             self.acceleration[1] + steering_force[1]]
        print(self.acceleration)
        self.check_collisions()

        self.current_direction = math.atan2(self.velocity[1], self.velocity[0])


    def update_time_spend(self):
        if self.current_task != Tasks.GatherAnts:
            self.time_spend += 1


    def update_position(self, boundaries):

        self.velocity = [self.velocity[0] + self.acceleration[0], self.velocity[1] + self.acceleration[1]]

        speed = math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        if speed > self.speed:
            self.velocity = [self.velocity[0] * self.speed / speed, self.velocity[1] * self.speed / speed]

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
            self.current_direction = math.atan2(self.velocity[1], self.velocity[0])

        # Reset acceleration
        self.acceleration = [0, 0]


    def drop_pheromones(self):

        if self.current_task == Tasks.GatherAnts:
            if self.p_drop == True:
                self.p_drop = False
                return Pheromone(self.position, 400, pheromone_type=PheromonesTypes.FoundFood,pheromone_strength=1)
            else:
                self.p_drop = True
