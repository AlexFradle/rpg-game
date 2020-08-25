import pygame


class Player:
    def __init__(self, pos, radius, colour, money):
        self.pos = pos
        self.radius = radius
        self.colour = colour
        self.money = money

    def draw(self, win):
        space = win.properties[self.pos]
        x, y = pygame.Rect(space.x, space.y, space.get_rect().w, space.get_rect().h).center
        pygame.draw.circle(win, self.colour, (x, y), self.radius)

    def move(self, amount):
        if self.pos + amount > 35:
            self.pos = (self.pos + amount) - 35
        else:
            self.pos += amount
