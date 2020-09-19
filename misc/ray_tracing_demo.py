import pygame
import pygame.gfxdraw
from math import sin, cos, atan2, degrees, radians
import os
from typing import Union, Iterable
from random import randint
from dataclasses import dataclass
pygame.init()


class Board(pygame.Surface):
    def __init__(self, w, h):
        super().__init__((w, h), pygame.SRCALPHA)
        self.width = w
        self.height = h

    def update(self):
        self.fill((0, 0, 0))


class Player(pygame.Rect):
    def __init__(self, x, y, w, h, fov):
        super().__init__(x, y, w, h)
        self.fov = fov


@dataclass
class Ray:
    x1: Union[int, float]
    y1: Union[int, float]
    x2: Union[int, float]
    y2: Union[int, float]
    r: int
    col: Union[list, tuple]


@dataclass
class Wall:
    x1: Union[int, float]
    y1: Union[int, float]
    x2: Union[int, float]
    y2: Union[int, float]


def line_collide(line_1_coords: Iterable, line_2_coords: Iterable) -> tuple:
    # Unpacking argument iterable
    x1, y1, x2, y2 = line_1_coords
    x3, y3, x4, y4 = line_2_coords

    # Calculating t and u
    t = ((((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))))
    u = -((((x1 - x2) * (y1 - y3)) - ((y1 - y2) * (x1 - x3))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))))

    # Calculating intersection coords
    px = x1 + (t * (x2 - x1))
    py = y1 + (t * (y2 - y1))

    return (px, py) if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0 else False


def colour_lerp(a: Union[tuple, list], b: Union[tuple, list], num_of_cols: int) -> tuple:
    for t in range(num_of_cols + 1):
        t /= num_of_cols
        c = (a[0] + (t * (b[0] - a[0])), a[1] + (t * (b[1] - a[1])), a[2] + (t * (b[2] - a[2])), a[3] + (t * (b[3] - a[3])))
        yield c


def set_rays(p: Player, rs: list, ws: list) -> list:
    """
    Sets new ray position
    Uses the equation:
        (x', y') = (x + r(cos(θ)), y + r(sin(θ)))
        where:
            r = ray length
            θ = angle
    :param p: Player object
    :param rs: List of rays
    :param ws: List of walls
    :return: Updated list of rays
    """
    mx, my = pygame.mouse.get_pos()
    mid_deg = degrees(atan2((p.x + (p.w // 2)) - mx, (p.y + (p.h // 2)) - my))
    l = mid_deg - (p.fov // 2) + 90
    for pos, ray in enumerate(rs):
        ray.x1 = p.x
        ray.y1 = p.y
        fx = p.x + (ray.r * cos(radians(l + pos)))
        fy = p.y - (ray.r * sin(radians(l + pos)))
        ray.x2 = fx
        ray.y2 = fy

        # Check if ray collides with any wall
        collide_points = []
        for w in ws:
            collide_coords = line_collide([ray.x1, ray.y1, fx, fy], [w.x1, w.y1, w.x2, w.y2])
            if collide_coords:
                collide_points.append(collide_coords)

        # Get closest collision
        if collide_points:
            ray.x2, ray.y2 = min(collide_points, key=lambda a: abs(a[0]-ray.x1) + abs(a[1]-ray.y1))

    return rs


font = pygame.font.SysFont("courier", 15, True)
os.environ["SDL_VIDEO_CENTERED"] = "1"

width = 1280
height = 720
display = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True
fps = 60
r_len = 300
fov = 120
show_walls = False

board = Board(width, height)
player = Player(500, 500, 50, 50, fov)
rays = [Ray(player.x, player.y, 0, 0, r_len, (255, 255, 255)) for _ in range(player.fov)]
walls = [Wall(randint(100, 1000), randint(100, 600), randint(200, 1200), randint(200, 700)) for _ in range(10)]
# cols = [int(i * (255 / player.fov)) for i in range(player.fov // 2)]
# cols = cols + list(reversed(cols))

cols = [i for i in colour_lerp((0, 0, 0, 0), (255, 255, 0, 255), player.fov // 2)]
cols = cols + list(reversed(cols))

while running:
    ms = clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                walls = [Wall(randint(100, 1000), randint(100, 600), randint(200, 1200), randint(200, 700)) for _ in range(10)]
            if event.key == pygame.K_e:
                show_walls = not show_walls

    for p, b in enumerate(pygame.mouse.get_pressed()):
        if p == 0 and b == 1:
            player.fov -= 10
        elif p == 2 and b == 1:
            player.fov += 10

    display.fill((0, 0, 0))
    board.update()

    player.x, player.y = pygame.mouse.get_pos()

    rays = set_rays(player, rays, walls)
    for w in walls:
        pygame.draw.line(board, (0, 0, 255), (w.x1, w.y1), (w.x2, w.y2))
        if show_walls:
            pygame.draw.line(display, (0, 255, 0), (w.x1, w.y1), (w.x2, w.y2))

    for rp in range(len(rays) - 1):
        pygame.gfxdraw.textured_polygon(display, [(rays[rp].x1, rays[rp].y1), (rays[rp].x2, rays[rp].y2), (rays[rp + 1].x2, rays[rp + 1].y2), (rays[rp].x1, rays[rp].y1)], board, 0, 0)
        pygame.gfxdraw.filled_polygon(display, [(rays[rp].x1, rays[rp].y1), (rays[rp].x2, rays[rp].y2), (rays[rp + 1].x2, rays[rp + 1].y2), (rays[rp].x1, rays[rp].y1)], cols[rp])

    pygame.display.update()

pygame.quit()

