import random
import sys

import pygame


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
        # Smoothly transition to the new direction using linear interpolation
        alpha = 0.1  # Adjust this value for smoother or faster transitions
        self.current_direction = (1 - alpha) * self.current_direction + alpha * new_direction

    def update_sensors(self):
        # Calculate sensor positions based on current direction
        for i in range(3):
            angle_offset = (i - 1) * self.sensor_spacing
            angle = self.current_direction + angle_offset
            self.sensors[i].x = self.x + self.sensor_dst * math.cos(angle)
            self.sensors[i].y = self.y + self.sensor_dst * math.sin(angle)

    def detect_objects(self, objects):
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


# Example usage
import math

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ant = Ant()
ant.search_for_food(100)


def draw(screen, ant, objects):
    # Draw ant
    pygame.draw.circle(screen, GREEN, (int(ant.x), int(ant.y)), radius=10)

    # Draw objects
    for obj in objects:
        pygame.draw.circle(screen, RED, (int(obj.x), int(obj.y)), radius=2)

    # Draw sensors and lines to detected objects
    for i, sensor_pos in enumerate(ant.sensors):
        # pygame.draw.circle(screen, BLACK, (int(sensor_pos.x), int(sensor_pos.y)), radius=3)
        # pygame.draw.circle(screen, BLACK, (int(sensor_pos.x), int(sensor_pos.y)), radius=int(ant.sensor_dst), width=1)

        angle_offset = (i - 1) * ant.sensor_spacing
        angle = ant.current_direction + angle_offset
        end_x = sensor_pos.x + ant.sensor_dst * math.cos(angle)
        end_y = sensor_pos.y + ant.sensor_dst * math.sin(angle)
        pygame.draw.line(screen, BLUE, (int(sensor_pos.x), int(sensor_pos.y)), (int(end_x), int(end_y)))
        # Draw detection radius around the sensor
        # pygame.draw.circle(screen, BLACK, (int(sensor_pos.x), int(sensor_pos.y)), radius=int(ant.sensor_size), width=1)

        ant.detect_objects(objects)
        # Draw lines from detected objects to the ant
        for obj_pos in ant.detected_objects:
            pygame.draw.line(screen, RED, (int(sensor_pos.x), int(sensor_pos.y)),
                             (int(obj_pos.x), int(obj_pos.y)), 2)

    for i in range(len(ant.sensors)):
        start_sensor_pos = ant.sensors[i]
        end_sensor_pos = ant.sensors[(i + 1) % len(ant.sensors)]  # Wrap around to the first sensor
        pygame.draw.line(screen, BLUE, (int(start_sensor_pos.x), int(start_sensor_pos.y)),
                         (int(end_sensor_pos.x), int(end_sensor_pos.y)))



def main():
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Ant Walking")

    ant = Ant()
    clock = pygame.time.Clock()
    objects = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                objects.append(pygame.Vector2(pos[0], pos[1]))

        # Randomize target position
        screen.fill(WHITE)
        ant.handle_movement()
        ant.update_sensors()
        ant.detect_objects(objects)
        draw(screen, ant, objects)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()