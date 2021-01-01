import pygame
from data_loader import DataLoader
from constants import *


class Item:
    def __init__(self, name: str) -> None:
        self.__name = name
        self.__data = DataLoader.possible_items[name]

    @property
    def name(self):
        return self.__name

    @property
    def data(self):
        return self.__data


class ItemDrop(pygame.Surface):
    def __init__(self, x: int, y: int, item: Item) -> None:
        self.__width = int((WINDOW_HEIGHT / 720) * ITEM_DROP_WIDTH)
        self.__height = int((WINDOW_HEIGHT / 720) * ITEM_DROP_HEIGHT)
        super().__init__((self.__width, self.__height), pygame.SRCALPHA)
        self.x = x
        self.y = y
        self.item = item
        self.image = pygame.image.load(f"{MAIN_ASSET_PATH}{item.name}.png")
        self.__pickup_frames = iter([
            pygame.image.load(f"{MAIN_ASSET_PATH}{item.data['rarity']}_{i}.png")
            for i in range(1, ITEM_DROP_FRAME_AMOUNT[item.data["rarity"]] + 1)
        ])
        self.__play_animation = True

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def update(self) -> None:
        """
        Updates the ItemDrop surface
        :return: None
        """
        self.fill(ITEM_DROP_BACKGROUND)
        if self.__play_animation:
            try:
                img = next(self.__pickup_frames)
            except StopIteration:
                img = self.image
                self.__play_animation = False
            self.blit(img, (0, 0))
        else:
            self.blit(self.image, (0, 0))
