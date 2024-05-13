# Example usage
import math
import sys

import pygame

from Ant import Ant

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