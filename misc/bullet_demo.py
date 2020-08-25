import pygame
import math
pygame.init()


def shoot(circle_x, circle_y, circle_radius, mouse_x, mouse_y, speed):
    cur_x, cur_y = circle_x, circle_y
    circle_eq = lambda x, y: (x - center_x)**2 + (y - center_y)**2

    # Calculate Euclidean distance from target pos to player pos
    dist = math.sqrt((mouse_x - circle_x) ** 2 + (mouse_y - circle_y) ** 2)

    # Calculate the number of times the line can be divided by the speed
    num_of_divisions = abs(dist / (1 - speed))

    cur_div = 1
    while circle_eq(cur_x, cur_y) < circle_radius**2:
        cur_x = circle_x + ((cur_div / num_of_divisions) * (mouse_x - circle_x))
        cur_y = circle_y + ((cur_div / num_of_divisions) * (mouse_y - circle_y))

        yield cur_x, cur_y

        cur_div += 1


width, height = 1024, 720
display = pygame.display.set_mode((width, height), pygame.SRCALPHA)
clock = pygame.time.Clock()

font = pygame.font.SysFont("Courier", 15, True)
running = True

radius = 250
center_x, center_y = width // 2, height // 2
mx, my = 0, 0
bullet_speed = 20
bullet_x, bullet_y = None, None
bullet_positions = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            bullet_positions = list(shoot(center_x, center_y, radius, mx, my, bullet_speed))

    if bullet_positions is not None:
        if len(bullet_positions) > 0:
            bullet_x, bullet_y = bullet_positions.pop(0)
        else:
            bullet_x, bullet_y = None, None

    display.fill((0, 0, 0))
    pygame.draw.circle(display, (255, 0, 0), (center_x, center_y), radius)
    if bullet_x is not None:
        pygame.draw.rect(display, (255, 255, 255), pygame.Rect(bullet_x, bullet_y, 10, 10))

    pygame.display.update()
    clock.tick(60)

pygame.quit()


