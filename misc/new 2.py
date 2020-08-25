import pygame
import os
import numpy as np
from typing import Union
pygame.init()

font = pygame.font.SysFont("courier", 15, True)


class Point:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def p(self):
        return self.x, self.y


def n_bezier_curve(points: list, num_of_divisions: int=100) -> list:
    lines = [(*points[a], *points[b]) for a, b in zip(range(len(points)), range(1, len(points)))]

    def get_section(line: Union[tuple, list]) -> list:
        return list((line[0] + ((t / num_of_divisions) * (line[2] - line[0])), line[1] + ((t / num_of_divisions) * (line[3] - line[1]))) for t in range(num_of_divisions))

    def quadratic_bezier_curve(line_1: Union[tuple, list], line_2: Union[tuple, list]) -> list:
        return [(l1[0] + ((t / num_of_divisions) * (l2[0] - l1[0])), l1[1] + ((t / num_of_divisions) * (l2[1] - l1[1]))) for l1, l2, t in zip(get_section(line_1), get_section(line_2), range(num_of_divisions))]

    if len(lines) > 2:
        all_points, depth = np.array([quadratic_bezier_curve(lines[a], lines[b]) for a, b in zip(range(len(lines)), range(1, len(lines)))]), 1
        while_index = lambda p, x: (p, *(x,) * depth)
        while len(all_points) > 2:
            all_points, depth = np.array([[get_section((*all_points[while_index(a, i)], *all_points[while_index(b, i)])) for i in range(num_of_divisions)] for a, b in zip(range(len(all_points)), range(1, len(all_points)))]), 2
        ql1, ql2 = all_points[0], all_points[1]
        return_index = lambda x, p: (*(x,) * depth, p)
        return [(ql1[return_index(t, 0)] + ((t / num_of_divisions) * (ql2[return_index(t, 0)] - ql1[return_index(t, 0)])),ql1[return_index(t, 1)] + ((t / num_of_divisions) * (ql2[return_index(t, 1)] - ql1[return_index(t, 1)])))for t in range(num_of_divisions)]
    else:
        return quadratic_bezier_curve(lines[0], lines[1])


os.environ["SDL_VIDEO_CENTERED"] = "1"

display = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
running = True
fps = 60
points = []
mouse_down = False
bezier_points = []

while running:
    ms = clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                points.append(Point(*pygame.mouse.get_pos(), 10))
            if event.key == pygame.K_BACKSPACE:
                points = []
            if event.key == pygame.K_RETURN:
                if len(points) >= 3:
                    # bezier_points = bezier_curve(points[0].p(), points[1].p(), points[2].p())
                    bezier_points = n_bezier_curve([p.p() for p in points])
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_down = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_down = True

    if mouse_down:
        mx, my = pygame.mouse.get_pos()
        for p in points:
            if pygame.Rect(p.x - p.r, p.y - p.r, p.r * 2, p.r * 2).collidepoint(mx, my):
                p.x = mx
                p.y = my

    display.fill((0, 0, 0))

    for p in points:
        pygame.draw.circle(display, (0, 0, 255), (p.x, p.y), p.r)

    if bezier_points:
        for bp in bezier_points:
            pygame.draw.circle(display, (255, 0, 0), (int(bp[0]), int(bp[1])), 2)

    pygame.display.update()

pygame.quit()