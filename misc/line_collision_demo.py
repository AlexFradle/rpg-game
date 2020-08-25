import pygame
import math
from random import randint
from typing import Iterable
pygame.init()


def line_collide(line_1_coords: Iterable, line_2_coords: Iterable) -> tuple:
    """
    Line-Line Collision using the equation:


            (x1 - x3)(y3 - y4) - (y1 - y3)(x3 - x4)
        t = ---------------------------------------
            (x1 - x2)(y3 - y4) - (y1 - y2)(x3 - x4)


              (x1 - x2)(y1 - y3) - (y1 - y2)(x1 - x3)
        u = - ---------------------------------------
              (x1 - x2)(y3 - y4) - (y1 - y2)(x3 - x4)


        (Px, Py) = (x1 + t(x2 - x1), y1 + t(y2 - y1))
                             or
        (Px, Py) = (x3 + u(x4 - x3), y3 + u(y4 - y3))


    t and u are used to turn the infinite lines into line segments

    t and u can also be used to determine if there is a collision before calculating coords because:
        0.0 ≤ t ≤ 1.0
        0.0 ≤ u ≤ 1.0
    if t or u is outside of this range then there is no collision

    :param line_1_coords: (x1, y1, x2, y2)
    :param line_2_coords: (x3, y3, x4, y4)
    :return: Collision coords
    """
    # Unpacking argument iterable
    x1, y1, x2, y2 = line_1_coords
    x3, y3, x4, y4 = line_2_coords

    # Calculating t and u
    t = ((((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4)))/(((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))))
    u = -((((x1 - x2) * (y1 - y3)) - ((y1 - y2) * (x1 - x3)))/(((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))))

    # Calculating intersection coords
    px = x1 + (t * (x2 - x1))
    py = y1 + (t * (y2 - y1))

    return (px, py) if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0 else None


def get_rect_lines(rect: pygame.Rect) -> list:
    return [
        (rect.x, rect.y),
        (rect.x + rect.w, rect.y),
        (rect.x + rect.w, rect.y + rect.h),
        (rect.x, rect.y + rect.h)
    ]


display = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()
running = True

line_1 = (100, 100, 200, 200)
line_2 = (200, 100, 100, 200)
show_lines = True

rect = pygame.Rect(100, 100, 50, 50)
show_rect = False
rect_width = 50
rect_height = 50

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_e:
                show_lines = not show_lines
                show_rect = not show_rect
            elif event.key == pygame.K_a:
                rect_width -= 5
                rect_height -= 5
            elif event.key == pygame.K_d:
                rect_width += 5
                rect_height += 5
            elif event.key == pygame.K_SPACE:
                line_1 = [randint(0, 500) for i in range(4)]
                if show_lines:
                    line_2 = [randint(0, 500) for i in range(4)]
                if show_rect:
                    # rect = pygame.Rect(randint(100, 400), randint(100, 400), randint(5, 100), randint(5, 100))
                    rect = pygame.Rect(*pygame.mouse.get_pos(), randint(5, 100), randint(5, 100))

    display.fill((0, 0, 0))

    pygame.draw.line(display, (255, 0, 0), (line_1[0], line_1[1]), (line_1[2], line_1[3]))
    if show_lines:
        pygame.draw.line(display, (0, 255, 0), (line_2[0], line_2[1]), (line_2[2], line_2[3]))

        intersection = line_collide(line_1, line_2)
        if intersection is not None:
            px, py = intersection
            pygame.draw.circle(display, (0, 0, 255), (int(px), int(py)), 7)
    else:
        rect = pygame.Rect(*pygame.mouse.get_pos(), rect_width, rect_height)
        r_lines = get_rect_lines(rect)
        r_lines.append(r_lines[0])
        for i in range(len(get_rect_lines(rect))):
            pygame.draw.line(display, (0, 255, 0), r_lines[i], r_lines[i + 1])
            line_2 = r_lines[i] + r_lines[i + 1]
            intersection = line_collide(line_1, line_2)
            if intersection is not None:
                px, py = intersection
                pygame.draw.circle(display, (0, 0, 255), (int(px), int(py)), 7)

    pygame.display.update()
    clock.tick(60)

pygame.quit()