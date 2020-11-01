import pygame
from random import randint
from constants import *
pygame.init()


class Wall(pygame.Rect):
    def __init__(self, x: int, y: int, used: int, orientation: int):
        # 1 = vertical, 2 = horizontal
        w = WALL_VERTICAL_WIDTH if orientation == 1 else WALL_HORIZONTAL_WIDTH
        h = WALL_VERTICAL_HEIGHT if orientation == 1 else WALL_HORIZONTAL_HEIGHT
        super().__init__(x, y, w, h)
        self.x = x
        self.y = y
        self.open_ = bool(used)


class Cell(pygame.Rect):
    def __init__(self, x: int, y: int):
        w, h = CELL_WIDTH, CELL_HEIGHT
        super().__init__(x, y, w, h)
        self.x = x
        self.y = y


class Door(pygame.Rect):
    def __init__(self, x: int, y: int, used: int, orientation: int, offset: int):
        # 1 = vertical, 2 = horizontal
        w = DOOR_VERTICAL_WIDTH if orientation == 1 else DOOR_HORIZONTAL_WIDTH
        h = DOOR_VERTICAL_HEIGHT if orientation == 1 else DOOR_HORIZONTAL_HEIGHT
        super().__init__(x, y, w, h)
        self.x = x + (0 if orientation == 1 else offset)
        self.y = y + (offset if orientation == 1 else 0)
        self.open_ = bool(used)
        self.offset = offset


class Board(pygame.Surface):
    def __init__(self, grid=None):
        super().__init__((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
        self.__width = BOARD_WIDTH
        self.__height = BOARD_HEIGHT
        self.__grid = self.load_maze(MAZE_PATH) if grid is None else grid
        self.x = 0
        self.y = 0
        cell_num = self.__grid[1].count("X")
        # All cell positions
        self.cell_pos = [[Cell(CELL_WIDTH * j + (WALL_VERTICAL_WIDTH * (j + 1)), CELL_HEIGHT * i + (WALL_HORIZONTAL_HEIGHT * (i + 1))) for j in range(cell_num)]
                         for i in range(cell_num)]
        # All horizontal walls
        self.hori_wall_pos = [[Wall(WALL_HORIZONTAL_WIDTH * j + WALL_VERTICAL_WIDTH, WALL_VERTICAL_HEIGHT * i, 1, 2) for j in range(cell_num)] for i in range(cell_num + 1)]
        # All vertical walls
        self.vert_wall_pos = [[Wall(WALL_HORIZONTAL_WIDTH * j, WALL_VERTICAL_HEIGHT * i + WALL_HORIZONTAL_HEIGHT, 1, 1) for j in range(cell_num + 1)] for i in range(cell_num)]
        # All horizontal doors
        self.hori_door_pos = [[Door(WALL_HORIZONTAL_WIDTH * (j // 2), WALL_VERTICAL_HEIGHT * (i // 2), 0 if self.__grid[i][j + 1] == "-" else 1, 2, randint(50, 200))
                              for j in range(0, len(self.__grid) - 1, 2)] for i in range(0, len(self.__grid), 2)]
        # All vertical doors
        self.vert_door_pos = [[Door(WALL_HORIZONTAL_WIDTH * (j // 2), WALL_VERTICAL_HEIGHT * (i // 2), 0 if self.__grid[i][j - 1] == "|" else 1, 1, randint(50, 200))
                              for j in range(1, len(self.__grid) + 1, 2)] for i in range(1, len(self.__grid), 2)]

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def grid(self):
        return self.__grid

    @staticmethod
    def load_maze(fn: str) -> list:
        """
        Loads maze created by maze_creator.py
        :param fn: File name to be loaded from
        :return: Maze without newline chars
        """
        with open(fn) as f:
            return [i.replace("\n", "") for i in f.readlines()]

    def door_collide(self, player):
        player_rect = pygame.Rect((player.x + (player.width // 2)) - self.x, (player.y + (player.height // 2)) - self.y, player.width, player.height)
        for row in self.vert_door_pos:
            for door in row:
                if door.y < player_rect.y < door.y + door.height and door.y < player_rect.y + player_rect.height < door.y + door.height:
                    if player_rect.colliderect(door):
                        return "door closed" if not door.open_ else "door open"

        for row in self.hori_door_pos:
            for door in row:
                if door.x < player_rect.x < door.x + door.width and door.x < player_rect.x + player_rect.width < door.x + door.width:
                    if player_rect.colliderect(door):
                        return "door closed"if not door.open_ else "door open"

        return "not on door"

    def wall_collide(self, player):
        player_rect = pygame.Rect((player.x + (player.width // 2)) - self.x, (player.y + (player.height // 2)) - self.y, player.width, player.height)
        for row in self.vert_wall_pos:
            for wall in row:
                if player_rect.colliderect(wall):
                    return True

        for row in self.hori_wall_pos:
            for wall in row:
                if player_rect.colliderect(wall):
                    return True

        return False

    def cell_collide(self, entity):
        entity_rect = pygame.Rect((entity.x + (entity.width // 2)) - self.x, (entity.y + (entity.height // 2)) - self.y, entity.width, entity.height)
        for r_pos, row in enumerate(self.cell_pos):
            for c_pos, cell in enumerate(row):
                if entity_rect.colliderect(cell):
                    return r_pos, c_pos

    def update(self) -> None:
        """
        Update the board
        :return: None
        """
        self.fill(BOARD_BACKGROUND)
        for hor in self.hori_wall_pos:
            for h in hor:
                pygame.draw.rect(self, WALL_COLOUR, h)
        for vert in self.vert_wall_pos:
            for v in vert:
                pygame.draw.rect(self, WALL_COLOUR, v)
        for door in self.hori_door_pos:
            for d in door:
                pygame.draw.rect(self, BOARD_BACKGROUND if d.open_ else DOOR_COLOUR, d)
        for door in self.vert_door_pos:
            for d in door:
                pygame.draw.rect(self, BOARD_BACKGROUND if d.open_ else DOOR_COLOUR, d)
        for row in self.cell_pos:
            for cell in row:
                pygame.draw.rect(self, BOARD_BACKGROUND, cell)
