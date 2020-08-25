import pygame
from misc.Monopoly.constants import *
pygame.init()


class Board(pygame.Surface):
    def __init__(self, width, height):
        super().__init__((width, height))
        self.properties = []
        temp = []
        for i in range(10):
            temp.append(Property(80 + (i * 60), 620, "property", 1500, "vert"))
        self.properties.extend(reversed(temp))
        temp = []
        for i in range(10):
            temp.append(Property(0, 80 + (i * 60), "property", 1500, "hoti"))
        self.properties.extend(reversed(temp))
        temp = []
        for i in range(10):
            temp.append(Property(80 + (i * 60), 0, "property", 1500, "vert"))
        self.properties.extend(temp)
        temp = []
        for i in range(10):
            temp.append(Property(620, 80 + (i * 60), "property", 1500, "hori"))
        self.properties.extend(temp)

    def draw(self):
        self.fill((200, 200, 255))
        for pos, p in enumerate(self.properties):
            p.draw(self, pos)


class Property(pygame.Surface):
    def __init__(self, x, y, name, price, orientation):
        super().__init__((PROPERTY_WIDTH, PROPERTY_HEIGHT))
        self.x = x
        self.y = y
        self.name = name
        self.price = price
        self.orientation = orientation

    def draw(self, win, pos):
        self.fill((200, 200, 255))
        width = PROPERTY_WIDTH if self.orientation == "vert" else PROPERTY_HEIGHT
        height = PROPERTY_HEIGHT if self.orientation == "vert" else PROPERTY_WIDTH
        pygame.draw.rect(win, BLACK, (self.x, self.y, width, height), 1)
        # Number text
        font = pygame.font.SysFont("courier", 15, True)
        win.blit(font.render(str(pos), True, (0, 0, 0)), (self.x, self.y))
