import pygame
import math
import os
import colour
from typing import Union
from random import randint
pygame.init()


def colour_lerp(a: Union[tuple, list], b: Union[tuple, list], num_of_cols: int) -> tuple:
    """
    Colour linear interpolation between c1 and c2
    Uses the equation:
        Cr = Ar + t(Br - Ar)
        Cg = Ag + t(Bg - Ag)
        Cb = Ab + t(Bb - Ab)

        0.0 ≤ t ≤ 1.0

        Where:
            A is the start colour,
            B is the end colour,
            C is the interpolated colour

    :param a:
    :param b:
    :param num_of_cols:
    :return:
    """
    for t in range(num_of_cols + 1):
        t /= num_of_cols
        c = (a[0] + (t * (b[0] - a[0])), a[1] + (t * (b[1] - a[1])), a[2] + (t * (b[2] - a[2])))
        yield c


class TeleportAnimation(pygame.Surface):
    def __init__(self, x, y):
        self.width = 400
        self.height = 60
        super().__init__((self.width, self.height), pygame.SRCALPHA)
        self.x = x
        self.y = y
        self.divs = 15
        self.segments = [pygame.Rect((self.width // self.divs) * i, 0, self.width // self.divs, self.height) for i in range(self.divs)]
        self.cur_frame = 0
        self.__colour_grad = [i for i in colour_lerp((255, 255, 255), (255, 60, 0), self.divs)]

    def update(self):
        # takes 30 frames
        self.fill((0, 255, 0, 60))
        if self.cur_frame < 15:
            for i in range(self.cur_frame):
                pygame.draw.rect(self, self.__colour_grad[i], self.segments[i])
            self.cur_frame += 1
        elif 15 <= self.cur_frame <= 30:
            for i in range(self.cur_frame - 15, 15):
                pygame.draw.rect(self, self.__colour_grad[i], self.segments[i])
            self.cur_frame += 1


font = pygame.font.SysFont("courier", 15, True)
os.environ["SDL_VIDEO_CENTERED"] = "1"

display = pygame.display.set_mode((1280, 1000))
clock = pygame.time.Clock()
running = True
fps = 60
tpa = TeleportAnimation(500, 500)

while running:
    ms = clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                tpa.cur_frame = 0
                tpa.x = randint(100, 600)
                tpa.y = randint(100, 600)

    display.fill((0, 0, 0))

    tpa.update()

    tpa_90 = pygame.transform.rotate(tpa, 90)
    tpa_180 = pygame.transform.rotate(tpa, 180)
    tpa_270 = pygame.transform.rotate(tpa, 270)

    display.blit(tpa_90, (tpa.x, tpa.y - tpa.width))
    display.blit(tpa_180, (tpa.x - tpa.width, tpa.y))
    display.blit(tpa_270, (tpa.x, tpa.y + tpa.height))
    display.blit(tpa, (tpa.x + tpa.height, tpa.y))

    pygame.display.update()

pygame.quit()
