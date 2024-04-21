import time as tm
from enum import Enum
import math
import random
import numpy as np
import pygame

from Settings import Settings


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)

    def normalized(self):
        magnitude = math.sqrt(self.x ** 2 + self.y ** 2)
        if magnitude == 0:
            return Vec2(0, 0)
        return Vec2(self.x / magnitude, self.y / magnitude)

    def clamp_magnitude(self, max_magnitude):
        magnitude = math.sqrt(self.x ** 2 + self.y ** 2)
        if magnitude > max_magnitude:
            return self.normalized() * max_magnitude
        return self

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)


class Tasks(Enum):
    FindHome = 1
    FindFood = 2


class Ant:
    def __init__(self, x=100, y=100, speed=0.00, steering=0, wandering_strength=0):
        self.x = x
        self.y = y
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

        self.detected_objects = []

    def random_steering(self):
        # Generate a random angle between 0 and 2*pi
        angle = random.uniform(0, 2 * math.pi)
        # Adjust the angle to make the movement less jittery
        angle += random.uniform(-self.steering, self.steering)
        return angle



    def handle_movement(self):
        """
        Handles the movement of the ant, updating its direction and position. OLD VERSION, USE PERIODIC MOVEMENT INSTEAD
        """
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
        self.x += self.speed * math.cos(self.current_direction)
        self.y += self.speed * math.sin(self.current_direction)

    def interpolate_direction(self, new_direction):
        """
        Function that helps smooth change of direction. Makes it less abrupt.
        """
        # Smoothly transition to the new direction using linear interpolation
        alpha = 0.1  # Adjust this value for smoother or faster transitions
        self.current_direction = (1 - alpha) * self.current_direction + alpha * new_direction

    def update_sensors(self):
        """
        updates the sensor distance and angle.
        """
        # Calculate sensor positions based on current direction
        for i in range(3):
            angle_offset = (i - 1) * self.sensor_spacing
            angle = self.current_direction + angle_offset
            self.sensors[i].x = self.position[0] + self.sensor_dst * math.cos(angle)
            self.sensors[i].y = self.position[1] + self.sensor_dst * math.sin(angle)

    def detect_objects(self, objects):
        """
        checks if objects are within the sensor range and if so add them to detected object array.
        Objects range from pheromones to colony and food
        """
        self.detected_objects = []
        # Reset sensor data
        for i in range(3):
            self.sensor_data[i] = 0.0

        # Detect objects within sensor range
        for i, sensor_pos in enumerate(self.sensors):
            # Calculate angle of sensor relative to ant's direction
            angle_offset = (i - 1) * self.sensor_spacing
            angle = self.current_direction + angle_offset
            if -math.pi / 6 <= angle_offset <= math.pi / 6:
                for obj_pos in objects:
                    # Calculate angle between sensor and object
                    obj_angle = math.atan2(obj_pos.y - self.y, obj_pos.x - self.x)
                    # Calculate difference in angles
                    angle_diff = abs(obj_angle - angle)
                    # Wrap angle difference to range [-pi, pi]
                    angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
                    # Check if object is within detection angle range
                    if abs(angle_diff) < math.pi / 3:
                        # Calculate distance between sensor and object
                        dist = sensor_pos.distance_to(obj_pos)
                        if dist < self.sensor_size:
                            self.detected_objects.append(obj_pos)
                            # Update sensor data based on object proximity
                            self.sensor_data[i] = max(self.sensor_data[i], 1.0 - dist / self.sensor_size)

    def search_for_food(self, steps):
        print(f"Ant's position: ({self.x}, {self.y})")
        return self.handle_movement()


    def drop_pheromones(self):
        return NotImplemented


    def scan_radius(self):
        return NotImplemented

    def movement(self):
        return NotImplemented

    def check_collision(self):
        return NotImplemented

    def update_position(self):
        return NotImplemented


