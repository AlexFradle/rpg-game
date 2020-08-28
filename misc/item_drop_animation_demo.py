import pygame
from itertools import cycle
pygame.init()


width, height = 500, 500
display = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

font = pygame.font.SysFont("Courier", 15, True)
running = True
play_imgs = False

rarities = [("bronze", 26), ("silver", 26), ("gold", 26), ("diamond", 26)]
imgs = {i[0]: [pygame.image.load(f"assets/animation/{i[0]}/{i[0]}_{j + 1}.png") for j in range(i[1])] for i in rarities}
frames = None
rarities = cycle(rarities)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                play_imgs = True
                rarity = next(rarities)
                if rarity[0] == "large":
                    frames = iter(reversed(imgs[rarity[0]]))
                else:
                    frames = iter(imgs[rarity[0]])

    display.fill((0, 0, 0))

    if frames is not None:
        try:
            display.blit(next(frames), (250, 250))
        except StopIteration:
            pass

    pygame.display.update()
    clock.tick(60)

pygame.quit()

