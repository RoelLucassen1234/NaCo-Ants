from math import sin,cos, atan2, radians, degrees ,sqrt
import random
from Nest import Nest
from versionV2.Food import Food
from Pheromone import Pheromone, PheromonesTypes
from Task import Tasks


class Ant():
    def __init__(self, max_steering=1, exploration_prob=0.3, ph_decay=0.8, detection_range=70, position=[100, 100]):
        #IDX
        self.idx = random.randrange(1000,100000)

        self.position = position

        #movement
        self.acceleration = [0, 0]
        self.velocity = [0, 0]
        self.steering = 1
        self.angle = random.randint(0, 360)
        self.direction = [cos(radians(self.angle)), sin(radians(self.angle))]
        self.nest = position


        # Genetic Properties
        self.max_steering = max_steering
        self.exploration_prob = exploration_prob
        self.ph_decay = ph_decay
        self.detection_range = detection_range

        self.speed = 1.5
        self.fitness = 0

        # Detection
        self.detected_objects = []
        #Task
        self.current_task = Tasks.FindFood

        # Time
        self.time_spend = 0

        # limit of Food Pheromone
        self.limit = 100
        #Limit of Home pheromone
        self.limit_home_p = 40

        self.ph_max = 0 # Keeps track of how long pheromones have been dropping
        self.ph_tick = 20  # Dropping P every amount of frames
        self.p_drop_current = 0 #Checks at what frame it currently is

        # Statistics
        self.steps_to_home = 0
        self.initial_position = position
        self.test_steering = 0
        self.food_delivered = 0

    def scan_objects_in_radius(self, objects):
        self.detected_objects = []
        nearby_objects_around_ant = objects.get_objects_nearby(self)

        for obj in nearby_objects_around_ant:
            distance = sqrt((obj.position[0] - self.position[0]) ** 2 + (obj.position[1] - self.position[1]) ** 2)

            if distance < self.detection_range:
                self.detected_objects.append(obj)

        return self.detected_objects


    def search_target(self):
        """"Searches through all existing objects within a certain radius and tries to find either the oldest pheromone
        Or the Nest/ Food. Their own pheromones take priority."""
        oldest_pheromone_position = None
        oldest_pheromone_age = float('inf')

        ant_pheromone_position = None
        ant_pheromone_oldest_pheromone_age = float('inf')

        for obj in self.detected_objects:
            if self.current_task == Tasks.FindFood and isinstance(obj,Food):
                return obj.position
            elif isinstance(obj, Pheromone):
                if self.current_task == Tasks.FindHome and obj.pheromone_type == PheromonesTypes.FoundHome:
                    if obj.ant_p == self.idx and obj.current_strength < ant_pheromone_oldest_pheromone_age:
                        ant_pheromone_position = obj.position
                        ant_pheromone_oldest_pheromone_age = obj.current_strength
                    elif obj.current_strength < oldest_pheromone_age:
                        oldest_pheromone_age = obj.current_strength
                        oldest_pheromone_position = obj.position
                elif self.current_task == Tasks.FindFood and obj.pheromone_type == PheromonesTypes.FoundFood:
                    if obj.ant_p == self.idx and obj.current_strength < ant_pheromone_oldest_pheromone_age:
                        ant_pheromone_position = obj.position
                        ant_pheromone_oldest_pheromone_age = obj.current_strength
                    elif obj.current_strength < oldest_pheromone_age:
                        oldest_pheromone_age = obj.current_strength
                        oldest_pheromone_position = obj.position

        if ant_pheromone_position:
            return ant_pheromone_position
        return oldest_pheromone_position


    def calculate_sensor_points(self):
        """"Calculates the sensor locations in front of the ant usually after movement. There are 3 sensor points."""
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
        # print(len(nearby_objects_around_ant))

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
                    self.food_delivered += 1
                    return True


    def in_radius_of_food_or_nest(self, radius = 80):

        if self.current_task == Tasks.FindHome:
            distance = sqrt((self.nest[0] - self.position[0]) ** 2 + (self.nest[1] - self.position[1]) ** 2)
            # Check if the distance is within the radius
            if distance <= radius:
                return self.nest

    def move_direction_update(self, boundaries):
        # Determine target direction
        target = self.in_radius_of_food_or_nest() or self.search_target()
        if target:
            target_direction = [(target[0] - self.position[0]), (target[1] - self.position[1])]
            target_magnitude = sqrt(target_direction[0] ** 2 + target_direction[1] ** 2)
            if target_magnitude != 0:
                target_direction = [target_direction[0] / target_magnitude, target_direction[1] / target_magnitude]
            self.direction = [(self.direction[0] + (target_direction[0] - self.direction[0]) * 0.1),
                              (self.direction[1] + (target_direction[1] - self.direction[1]) * 0.1)]
        else:
            random_angle = radians(random.randint(0, 360))
            random_direction = [cos(random_angle), sin(random_angle)]
            self.direction = [self.direction[0] + random_direction[0] * self.exploration_prob,
                              self.direction[1] + random_direction[1] * self.exploration_prob]

        # Normalize direction
        direction_magnitude = sqrt(self.direction[0] ** 2 + self.direction[1] ** 2)
        if direction_magnitude != 0:
            self.direction = [self.direction[0] / direction_magnitude, self.direction[1] / direction_magnitude]

        # Calculate desired velocity and steering force
        desired_velocity = [self.direction[0] * self.speed, self.direction[1] * self.speed]
        steering_force = [(desired_velocity[0] - self.velocity[0]) * self.max_steering,
                          (desired_velocity[1] - self.velocity[1]) * self.max_steering]

        # Normalize steering force
        steering_magnitude = sqrt(steering_force[0] ** 2 + steering_force[1] ** 2)
        if steering_magnitude > self.steering:
            steering_force = [steering_force[0] / steering_magnitude * self.max_steering,
                              steering_force[1] / steering_magnitude * self.max_steering]

        # Update velocity
        self.velocity = [self.velocity[0] + steering_force[0],
                         self.velocity[1] + steering_force[1]]

        # Normalize velocity
        velocity_magnitude = sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)
        if velocity_magnitude > self.speed:
            self.velocity = [self.velocity[0] / velocity_magnitude * self.speed,
                             self.velocity[1] / velocity_magnitude * self.speed]

        # Update position
        new_position = [self.position[0] + self.velocity[0],
                        self.position[1] + self.velocity[1]]

        # Boundary check
        if (boundaries[0][0] <= new_position[0] <= boundaries[1][0]) and (
                boundaries[0][1] <= new_position[1] <= boundaries[1][1]):
            self.position = new_position
        else:
            self.velocity = [-self.velocity[0], -self.velocity[1]]
            self.direction = [-self.direction[0], -self.direction[1]]

        # Collision check
        if self.check_collisions():
            self.direction = [-self.direction[0], -self.direction[1]]
            self.angle = degrees(atan2(-self.velocity[1], -self.velocity[0]))
        else:
            self.angle = degrees(atan2(self.velocity[1], self.velocity[0]))

        self.acceleration = [0, 0]

    def drop_pheromones(self):
        # Check current task and conditions for dropping pheromones
        if self.current_task == Tasks.FindFood:
            if self.ph_tick == self.p_drop_current and self.ph_max < self.limit_home_p:
                # Reset drop timer and increase pheromone count
                self.p_drop_current = 0
                self.ph_max += 1
                # Create and return a pheromone object for finding home
                return Pheromone(self.position, lifetime=600, pheromone_type=PheromonesTypes.FoundHome, pheromone_strength=self.ph_decay, a_idx=self.idx)
            else:
                self.p_drop_current += 1

        elif self.current_task == Tasks.FindHome:
            if self.ph_tick == self.p_drop_current and self.ph_max < self.limit:
                # Reset drop timer and increase pheromone count
                self.p_drop_current = 0
                self.ph_max += 1
                # Create and return a pheromone object for finding food
                return Pheromone(self.position, lifetime=1000, pheromone_type=PheromonesTypes.FoundFood,
                                pheromone_strength =self.ph_decay, a_idx=self.idx)
            else:
                self.p_drop_current += 1

    def set_fitness(self, val):
        self.fitness = val
