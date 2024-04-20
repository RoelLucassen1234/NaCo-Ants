import pygame
import sys

from Ant import Ant

x = 100
y = 100

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)


def draw(screen, ant):
    pygame.draw.circle(screen, GREEN, ant.pos,radius=20)


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Ant Walking")

    ant = Ant(x,y)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(WHITE)
        # ant.update()
        draw(screen, ant)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()