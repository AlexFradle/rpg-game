import pygame
from time import sleep

pygame.init()
display = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()
running = True

mv_amount = 5
fps = 60

while running:
    ms = clock.tick(fps)
    ms_per_frame = 1000 / fps
    print("tick =", ms)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    display.fill((0, 0, 0))

    print("proper =", ms_per_frame)
    print("mv_every_sec =", mv_amount * fps)
    print("delta_time =", ms / ms_per_frame)
    print("new_mv_amount =", mv_amount * (ms / ms_per_frame))
    print()

    sleep(0.2)

    pygame.display.update()

pygame.quit()