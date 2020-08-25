import pygame
import math
from random import randint
pygame.init()


class SubdividedCircle(pygame.Surface):
    def __init__(self, diameter, sec_num):
        super().__init__((diameter, diameter))
        self.radius = diameter // 2
        self.diameter = diameter
        self.sectors = [
            (
                math.radians(0 + ((360 / sec_num) * i)),
                math.radians(0 + ((360 / sec_num) * (i + 1))),
                (randint(0, 255), randint(0, 255), randint(0, 255))
            )
            for i in range(sec_num)
        ]
        self.is_spinning = False

    def update(self):
        self.fill((0, 0, 0))
        for pos, sect in enumerate(self.sectors):
            if self.is_spinning:
                self.sectors[pos] = (self.sectors[pos][0] + 0.1, self.sectors[pos][1] + 0.1, self.sectors[pos][2])
            pygame.draw.arc(self, self.sectors[pos][2], pygame.Rect(0, 0, self.diameter, self.diameter), self.sectors[pos][0], self.sectors[pos][1], self.radius)


display = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()

sub_divides = 1
sc = SubdividedCircle(500, sub_divides)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                sub_divides += 1
                sc = SubdividedCircle(500, sub_divides)
            if event.button == 3:
                sc.is_spinning = True

    display.fill((0, 0, 0))

    sc.update()
    display.blit(sc, (0, 0))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
