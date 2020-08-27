import pygame
import os
from typing import Union

pygame.init()


class Point:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def p(self):
        return self.x, self.y


class Button(pygame.Surface):
    def __init__(self, x, y, w, h, txt, func):
        super().__init__((w, h))
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.txt = txt
        self.rendered_txt = font.render(txt, True, (0, 0, 0))
        self.func = func

    def update(self):
        self.fill((255, 255, 255))
        self.blit(self.rendered_txt, (0, 0))


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


def get_point_rgb(p1, p2, p3):
    red, green, blue = 0, 0, 0
    for r in red_grad:
        if r[0].collidepoint(p1.x, p1.y):
            red = r[1][0]
            break

    for g in green_grad:
        if g[0].collidepoint(p2.x, p2.y):
            green = g[1][1]
            break

    for b in blue_grad:
        if b[0].collidepoint(p3.x, p3.y):
            blue = b[1][2]
            break

    return red, green, blue


def set_a(col):
    global colour_a
    colour_a = col


def set_b(col):
    global colour_b
    colour_b = col


def set_lerp_grad(cols):
    global lerp_grad
    lerp_grad = [i for i in cols]


font = pygame.font.SysFont("courier", 15, True)
os.environ["SDL_VIDEO_CENTERED"] = "1"

display = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
running = True
fps = 60
red_grad = [(pygame.Rect(10 + (2 * i), 75, 2, 50), (i, 0, 0)) for i in range(256)]
green_grad = [(pygame.Rect(10 + (2 * i), 275, 2, 50), (0, i, 0)) for i in range(256)]
blue_grad = [(pygame.Rect(10 + (2 * i), 475, 2, 50), (0, 0, i)) for i in range(256)]

colour_a = []
colour_b = []
lerp_grad = []

points = [
    Point(10, 100, 15),
    Point(10, 300, 15),
    Point(10, 500, 15)
]
buttons = [
    Button(10, 700, 100, 50, "Set a", set_a),
    Button(120, 700, 100, 50, "Set b", set_b),
    Button(230, 700, 100, 50, "Do lerp", set_lerp_grad)
]
mouse_down = False

while running:
    ms = clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                pass
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_down = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_down = True
            mx, my = pygame.mouse.get_pos()
            for button in buttons:
                if pygame.Rect(button.x, button.y, button.w, button.h).collidepoint(mx, my):
                    print(button.txt)
                    button.func(get_point_rgb(*points) if button.txt in ["Set a", "Set b"] else colour_lerp(colour_a, colour_b, 100))

    if mouse_down:
        mx, my = pygame.mouse.get_pos()
        for p in points:
            if pygame.Rect(p.x - p.r, p.y - p.r, p.r * 2, p.r * 2).collidepoint(mx, my):
                p.x = mx if 10 <= mx <= 522 else p.x

    display.fill((0, 0, 0))

    for r in red_grad:
        pygame.draw.rect(display, r[1], r[0])

    for g in green_grad:
        pygame.draw.rect(display, g[1], g[0])

    for b in blue_grad:
        pygame.draw.rect(display, b[1], b[0])

    current_rgb = get_point_rgb(*points)
    rgb_txt = font.render(f"({current_rgb[0]}, {current_rgb[1]}, {current_rgb[2]})", True, (255, 255, 255))
    display.blit(rgb_txt, (10, 600))

    pygame.draw.rect(display, current_rgb, pygame.Rect(472, 600, 50, 50))

    for but in buttons:
        but.update()
        display.blit(but, (but.x, but.y))

    for p in points:
        pygame.draw.circle(display, (255, 255, 255), (p.x, p.y), p.r)

    if lerp_grad:
        height = 450 // len(lerp_grad)
        for pos, lg in enumerate(lerp_grad):
            pygame.draw.rect(display, lg, pygame.Rect(600, 75 + (height * pos), 50, height))

    pygame.display.update()

pygame.quit()
