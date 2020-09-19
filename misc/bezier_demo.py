import pygame
import pygame.gfxdraw
import os
from dataclasses import dataclass
from compiled_funcs import bezier
pygame.init()


@dataclass
class Bezier:
    control_points: list
    num_of_points: int

    def get_points(self):
        control_x, control_y = zip(*self.control_points)
        return [
            (
                int(self.__B(control_x, 0, len(self.control_points) - 1, t / self.num_of_points)),
                int(self.__B(control_y, 0, len(self.control_points) - 1, t / self.num_of_points))
            )
            for t in range(self.num_of_points + 1)
        ]

    def __B(self, arr, i, j, t):
        """
        Using De Casteljau's algorithm:
        Gets the one dimensional value of the coords at the provided i value
        Recurrence relation:
            B(i, j) = B(i, j - 1) * (1 - t) + B(i + 1, j - 1) * t
        """
        return arr[i] if j == 0 else self.__B(arr, i, j - 1, t) * (1 - t) + self.__B(arr, i + 1, j - 1, t) * t


font = pygame.font.SysFont("courier", 15, True)
os.environ["SDL_VIDEO_CENTERED"] = "1"

display = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
fps = 60
start = None
end = None
c_points = []
nop = 100
b_points = None

while running:
    ms = clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                c_points.append(pygame.mouse.get_pos())
            if event.key == pygame.K_s:
                start = pygame.mouse.get_pos()

    end = pygame.mouse.get_pos()

    display.fill((0, 0, 0))

    for c in c_points:
        pygame.draw.circle(display, (255, 255, 255), c, 7)

    if c_points:
        # b_points = Bezier([start] + c_points + [end], nop).get_points()
        b_points = bezier([start] + c_points + [end], nop)

    if b_points:
        for b in b_points:
            pygame.draw.circle(display, (0, 0, 255), b, 7)

    if start is not None:
        pygame.draw.circle(display, (0, 255, 0), start, 7)
    pygame.draw.circle(display, (255, 0, 0), end, 7)

    # if b_points:
    #     pygame.gfxdraw.textured_polygon(display, b_points, pygame.image.load("diamond_1.png"), 0, 0)

    fps_txt = font.render(str(round(clock.get_fps(), 0)), True, (0, 255, 0))
    display.blit(fps_txt, (0, 0))

    pygame.display.update()

pygame.quit()