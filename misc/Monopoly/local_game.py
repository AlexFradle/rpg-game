import pygame
import sys
from misc.Monopoly.player import Player
from misc.Monopoly.board import Board
import random
from misc.Monopoly.constants import *
pygame.init()

pygame.display.set_caption("Monopoly")
win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()


def dice_roll():
    return random.randint(2, 12)


board = Board(WINDOW_WIDTH, WINDOW_HEIGHT)
p1 = Player(0, 14, RED, 1500)
run = True
turn = 0

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            p1.move(dice_roll())

        win.fill((200, 200, 255))

        board.draw()
        p1.draw(board)

        win.blit(board, (0, 0))

        pygame.display.update()
        clock.tick(60)

pygame.quit()
