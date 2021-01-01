import pygame
from data_loader import DataLoader
from itertools import chain
from constants import *
from xml.etree.ElementTree import Element
from typing import Union, Optional
from time import time


class Hotbar(pygame.Surface):
    """Displays what the player has in their hotbar"""
    def __init__(self) -> None:
        super().__init__((WINDOW_WIDTH // 3, WINDOW_HEIGHT // 10), pygame.SRCALPHA)
        self.__width = WINDOW_WIDTH // 3
        self.__height = WINDOW_HEIGHT // 10
        self.inv_size = 5
        self.__items = self.__get_items()
        self.__selected_pos = 0
        space_in = 9
        self.__item_spaces = [
            pygame.Rect(
                space_in + ((self.__width // self.inv_size) * i),
                space_in,
                (self.__width // self.inv_size) - (space_in * 2),
                self.__height - (space_in * 2)
            ) for i in range(self.inv_size)
        ]

    def __setitem__(self, key, value):
        if key < len(self.__items):
            self.__items[key] = value

    def __getitem__(self, item: int) -> tuple:
        """
        Gets the item image and name at the given position
        :param item: The item to be gotten
        :return: (pygame.image, name)
        """
        return self.__items[item]

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def selected_pos(self):
        return self.__selected_pos

    @selected_pos.setter
    def selected_pos(self, value: int) -> None:
        self.__selected_pos = value if isinstance(value, int) else self.__selected_pos

    def __get_items(self) -> list:
        """
        Gets all items in hotbar
        :return: list of all items and their images, e.g (fire.png, fire)
        """
        return list(map(
            lambda x: (pygame.image.load(f"{MAIN_ASSET_PATH}{x}.png"), x),
            [
                "no_item" if DataLoader.player_data["hotbar"][i] is None else DataLoader.player_data["hotbar"][i]
                for i in range(self.inv_size)
            ]
        ))

    def update(self) -> None:
        """
        Update the hotbar
        :return: None
        """
        # Fill create background colour
        self.fill(HOTBAR_BACKGROUND)

        # Get current items
        self.__items = self.__get_items()

        # Loop through spaces to draw
        for pos, space in enumerate(self.__item_spaces):
            # Surrounding colour depending on rarity
            col = DataLoader.rarities[DataLoader.possible_items[self.__items[pos][1]]["rarity"]]
            pygame.draw.rect(self, col, space)
            if pos == self.__selected_pos:
                pygame.draw.rect(self, (255, 255, 255), space, 5)

            # If that space is used then draw picture
            if self.__items[pos] is not None:
                self.blit(self.__items[pos][0], ((space.x + (space.w // 2)) - (self.__items[pos][0].get_width() // 2), (space.y + (space.h // 2)) - (self.__items[pos][0].get_height() // 2)))

    def change_selected(self, amount: int) -> None:
        """
        Changes the selected position on the hotbar
        :param amount: Amount of spaces to be incremented
        :return: None
        """
        self.__selected_pos += amount
        if self.__selected_pos == -1:
            self.__selected_pos = self.inv_size - 1
        elif self.__selected_pos == self.inv_size:
            self.__selected_pos = 0


class Inventory(pygame.Surface):
    """Displays the players current inventory"""
    def __init__(self) -> None:
        super().__init__((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), pygame.SRCALPHA)
        self.__width = WINDOW_WIDTH // 2
        self.__height = WINDOW_HEIGHT // 2
        self.inv_size = 20
        self.__items = self.__get_items()
        space_in = 9
        row_num = 5
        col_num = 4
        self.__item_spaces = list(chain.from_iterable([[
            pygame.Rect(
                space_in + ((self.__width // row_num) * j),
                space_in + ((self.__height // col_num) * i),
                (self.__width // (self.inv_size // 4)) - (space_in * 2),
                (self.__height // 4) - (space_in * 2)
            ) for j in range(row_num)] for i in range(col_num)
        ]))

    def __setitem__(self, key, value):
        if key < len(self.__items):
            self.__items[key] = value

    def __getitem__(self, item: int) -> tuple:
        """
        Gets the items in the spaces and the rect
        :param item: The item to be gotten
        :return: ((pygame.image, name), pygame.Rect)
        """
        return self.__items[item], self.__item_spaces[item]

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def __get_items(self) -> list:
        """
        Gets all items in inventory
        :return: list of all items and their images, e.g (fire.png, fire)
        """
        return list(map(
            lambda x: (pygame.image.load(f"{MAIN_ASSET_PATH}{x}.png"), x),
            [
                "no_item" if DataLoader.player_data["inventory"][i] is None else DataLoader.player_data["inventory"][i]
                for i in range(self.inv_size)
            ]
        ))

    def update(self, data: dict) -> None:
        """
        Update the inventory
        :param data: Dict containing the current item the mouse is over
        :return: None
        """
        # Fill create background colour
        self.fill(INV_BACKGROUND)

        # Get items in inv
        self.__items = self.__get_items()

        # Loop through spaces to draw
        for pos, space in enumerate(self.__item_spaces):
            # Surrounding colour depending on rarity
            col = DataLoader.rarities[DataLoader.possible_items[self.__items[pos][1]]["rarity"]]
            pygame.draw.rect(self, col, space)

            # Draw the border on the current hovered over item
            if data is not None:
                if pos == data["inv_pos"]:
                    pygame.draw.rect(self, INV_SELECTED, space, 5)

            # If that space is used then draw picture
            if self.__items[pos] is not None:
                self.blit(
                    self.__items[pos][0],
                    (
                        (space.x + (space.w // 2)) - (self.__items[pos][0].get_width() // 2),
                        (space.y + (space.h // 2)) - (self.__items[pos][0].get_height() // 2)
                    )
                )


class Inspector(pygame.Surface):
    """Provides information about the selected item"""
    def __init__(self) -> None:
        super().__init__((WINDOW_WIDTH // 5, WINDOW_HEIGHT // 1.5), pygame.SRCALPHA)
        self.__width = WINDOW_WIDTH // 5
        self.__height = WINDOW_HEIGHT // 1.5

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def update(self, name: str, font: pygame.font.Font, data: dict) -> None:
        """
        Updates inspector surface each frame
        :param name: Name of the item being inspected
        :param font: Font used to write the text
        :param data: Dict containing data, e.g {'img': pygame.image, 'attr': {..., ...}}
        :return: None
        """
        self.fill(INSPECTOR_BACKGROUND)
        if data is not None:
            if data["st_pos"] is not None:
                rarity_col = (0, 0, 0)
            else:
                rarity_col = DataLoader.rarities[data["attr"]["rarity"]]

            # Draw border of inspector with colour of item rarity
            pygame.draw.rect(self, rarity_col, pygame.Rect(0, 0, self.__width, self.__height), 5)

            # Draw background of image location
            pygame.draw.rect(self, rarity_col, pygame.Rect(self.__width // 2 - (data["img"].get_width() // 2), 10, data["img"].get_width(), data["img"].get_height()))

            # Draw name with underline
            font.set_underline(True)
            self.blit(font.render(name, True, TEXT_COLOUR), (self.__width // 2 - (font.size(name)[0] // 2), 90))
            font.set_underline(False)

            # If there is data provided, loop through and draw it
            self.blit(data["img"], (self.__width // 2 - (data["img"].get_width() // 2), 10))
            for pos, k in enumerate(data["attr"]):
                self.blit(font.render(f"{k}: {data['attr'][k]}", True, TEXT_COLOUR), (10, 110 + (20 * pos)))


class Equipment(pygame.Surface):
    """Displays the players current equipment"""
    def __init__(self) -> None:
        super().__init__((WINDOW_WIDTH // 5, WINDOW_HEIGHT // 1.5), pygame.SRCALPHA)
        self.__width = WINDOW_WIDTH // 5
        self.__height = WINDOW_HEIGHT // 1.5
        self.__imgs = self.__get_imgs()
        self.__slots = [pygame.Rect(self.__width // 2 - (i.get_width() // 2), (self.__height // 6) * (pos + 1), i.get_width(), i.get_height()) for pos, i in enumerate(self.__imgs)]
        self.__armor_names = self.__get_armor_names()

    def __getitem__(self, item):
        return (self.__imgs[item], self.__armor_names[item]), self.__slots[item]

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @staticmethod
    def __get_imgs() -> list:
        """
        Get armor images
        :return: List of loaded images
        """
        return [
            pygame.image.load(f"{MAIN_ASSET_PATH}{DataLoader.player_data['armor'][i]}.png")
            for i in ["head", "chest", "legs", "feet"]
        ]

    @staticmethod
    def __get_armor_names() -> list:
        """
        Get current equipped armor names
        :return: List of armor names
        """
        return list(DataLoader.player_data["armor"].values())

    def update(self, font: pygame.font.Font, data: dict) -> None:
        """
        Updates the Equipment surface
        :param font: Font to be used to render the text
        :param data: Dict containing the current item the mouse is over
        :return: None
        """
        self.fill(EQUIPMENT_BACKGROUND)

        # Get current equipped armour imgs and names
        self.__imgs = self.__get_imgs()
        self.__armor_names = self.__get_armor_names()

        # Draw outer border
        pygame.draw.rect(self, EQUIPMENT_BORDER, pygame.Rect(0, 0, self.__width, self.__height), 5)

        # Create defense and coin strings
        defense = f"Defense: {str(sum([DataLoader.possible_items[i]['defense'] for i in self.__armor_names]))}"
        coins = f"Coins: {DataLoader.player_data['coins']}"

        # Draw the defense text
        self.blit(
            font.render(defense, True, TEXT_COLOUR),
            (5, self.__height - font.size(defense)[1])
        )
        # Draw the coins text
        self.blit(
            font.render(coins, True, COIN_TEXT_COLOUR),
            (self.__width - font.size(coins)[0] - 5, self.__height - font.size(defense)[1])
        )
        # Have to use pos like this as you cant enumerate the loop
        pos = 0

        # Draw the armour slots
        for slot, img, armor in zip(self.__slots, self.__imgs, self.__armor_names):
            pygame.draw.rect(self, DataLoader.rarities[DataLoader.possible_items[armor]["rarity"]], slot)
            self.blit(img, slot)
            if data is not None:
                if pos == data["eq_pos"]:
                    pygame.draw.rect(self, EQUIPMENT_SELECTED, slot, 5)
            pos += 1


class HealthBar(pygame.Surface):
    """Displays the players current health in bar form"""
    def __init__(self, max_health: int) -> None:
        super().__init__((WINDOW_WIDTH // 5, WINDOW_HEIGHT // 20), pygame.SRCALPHA)
        self.__width = WINDOW_WIDTH // 5
        self.__height = WINDOW_HEIGHT // 20
        self.__max_health = max_health

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def update(self, font: pygame.font.Font, player_health: int) -> None:
        """
        Updates health bar surface
        :param font: Font to be used to render the text
        :param player_health: Amount of health the player has
        :return: None
        """
        self.fill((0, 0, 0, 0))

        # Amount of health left
        health_txt = str(int((player_health / self.__max_health) * self.__max_health))

        # Border for health bar
        pygame.draw.rect(self, HEALTHBAR_BACKGROUND_COLOUR, pygame.Rect(0, 0, self.__width - font.size(health_txt)[0], self.__height), 2)

        # Main bar that shows amount
        pygame.draw.rect(self, HEALTHBAR_BACKGROUND_COLOUR, pygame.Rect(0, 0, (self.__width - font.size(health_txt)[0]) * (player_health / self.__max_health), self.__height))
        self.blit(font.render(health_txt, True, HEALTHBAR_TEXT_COLOUR), (self.__width - font.size(health_txt)[0], self.__height // 4))


class ManaBar(pygame.Surface):
    """Displays the players current mana in bar form"""
    def __init__(self, max_mana: int) -> None:
        super().__init__((WINDOW_WIDTH // 5, WINDOW_HEIGHT // 20), pygame.SRCALPHA)
        self.__width = WINDOW_WIDTH // 5
        self.__height = WINDOW_HEIGHT // 20
        self.__max_mana = max_mana

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def update(self, font: pygame.font.Font, player_mana: int) -> None:
        """
        Updates mana bar surface
        :param font: Font to be used to render the text
        :param player_mana: The amount of mana the player has
        :return: None
        """
        self.fill((0, 0, 0, 0))

        # Amount of mana left
        health_txt = str(int((player_mana / self.__max_mana) * self.__max_mana))

        # Border for mana bar
        pygame.draw.rect(self, MANABAR_BACKGROUND_COLOUR, pygame.Rect(font.size(health_txt)[0], 0, self.__width - font.size(health_txt)[0], self.__height), 2)

        # Main bar that shows amount
        pygame.draw.rect(self, MANABAR_BACKGROUND_COLOUR, pygame.Rect(font.size(health_txt)[0], 0, (self.__width - font.size(health_txt)[0]) * (player_mana / self.__max_mana), self.__height))
        self.blit(font.render(health_txt, True, MANABAR_TEXT_COLOUR), (0, self.__height // 4))


class Attributes(pygame.Surface):
    """Displays the players current attributes"""
    def __init__(self) -> None:
        super().__init__((WINDOW_WIDTH // 5, WINDOW_HEIGHT // 1.5), pygame.SRCALPHA)
        self.__width = WINDOW_WIDTH // 5
        self.__height = WINDOW_HEIGHT // 1.5
        self.__plus_img = pygame.image.load(f"{MAIN_ASSET_PATH}plus.png")
        self.__minus_img = pygame.image.load(f"{MAIN_ASSET_PATH}minus.png")
        self.__attr_data = DataLoader.player_data["attributes"]
        self.__button_size = int((WINDOW_HEIGHT / 720) * 25)
        self.__pluses = [pygame.Rect((self.__width // 2) + (self.__width // 8) + 10, (self.__height // 5) * (i + 1), self.__button_size, self.__button_size) for i in range(len(self.__attr_data))]
        self.__minuses = [pygame.Rect((self.__width // 2) + (self.__width // 8) + 10, ((self.__height // 5) * (i + 1)) + self.__button_size, self.__button_size, self.__button_size) for i in range(len(self.__attr_data))]

    def __getitem__(self, item: int):
        return self.__pluses[item], self.__minuses[item]

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def update(self, font: pygame.font.Font) -> None:
        """
        Updates the Attributes surface
        :param font: Font to be used to render the text
        :return: None
        """
        self.fill(ATTRIBURES_BACKGROUND)
        self.__attr_data = DataLoader.player_data["attributes"]

        # Draw outer border
        pygame.draw.rect(self, ATTRIBURES_BORDER, pygame.Rect(0, 0, self.__width, self.__height), 5)

        # Loop through attribute data
        for pos, key in enumerate(self.__attr_data):
            # Draw attr number box
            pygame.draw.rect(self, ATTRIBURES_BORDER, pygame.Rect(self.__width // 8, (self.__height // 5) * (pos + 1), self.__width // 2, self.__button_size * 2), 5)

            # Draw plus and minus images
            self.blit(self.__plus_img, self.__pluses[pos])
            self.blit(self.__minus_img, self.__minuses[pos])

            # Draw attr names and attr number text
            self.blit(
                font.render(key, True, TEXT_COLOUR),
                (((self.__width // 8) + (self.__width // 4)) - (font.size(key)[0] // 2), ((self.__height // 5) * (pos + 1)) - font.size(key)[1])
            )
            self.blit(
                font.render(str(self.__attr_data[key]), True, TEXT_COLOUR),
                (((self.__width // 8) + (self.__width // 4)) - (font.size(str(self.__attr_data[key]))[0] // 2), ((self.__height // 5) * (pos + 1)) + font.size(str(self.__attr_data[key]))[1])
            )

            # Draw remaining skill point indicator
            pygame.draw.rect(self, ATTRIBURES_SP_BORDER, pygame.Rect(self.__width // 5, self.__height - 30, (self.__width // 5) * 3, 25))
            self.blit(font.render(f"Unused SP: {DataLoader.player_data['unused_sp']}", True, TEXT_COLOUR), (self.__width // 5, self.__height - 25))


class Tab(pygame.Surface):
    """Tab to change between equipment and attributes menus"""
    def __init__(self) -> None:
        super().__init__((WINDOW_WIDTH // 5, WINDOW_HEIGHT // 12), pygame.SRCALPHA)
        self.__width = WINDOW_WIDTH // 5
        self.__height = WINDOW_HEIGHT // 12
        self.selected_equipment = True
        self.__sects = [pygame.Rect((self.__width // 2) * i, 0, self.__width // 2, self.__height) for i in range(2)]

    def __getitem__(self, item):
        return self.__sects[item]

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def update(self, font: pygame.font.Font) -> None:
        """
        Updates the Tab surface
        :param font: Font to be used to render the text
        :return: None
        """
        self.fill(TAB_BACKGROUND)

        # Draw each tab
        pygame.draw.rect(self, TAB_BORDER, self.__sects[0], 0 if self.selected_equipment else 2)
        pygame.draw.rect(self, TAB_BORDER, self.__sects[1], 0 if not self.selected_equipment else 2)

        # Draw text
        self.blit(
            font.render("Equipment", True, TAB_SELECTED_TEXT_COLOUR if self.selected_equipment else TEXT_COLOUR),
            ((self.__sects[0].w // 2) - (font.size("Equipment")[0] // 2), (self.__sects[0].y + (self.__sects[0].h // 2)) - (font.size("Equipment")[1] // 2))
        )
        self.blit(
            font.render("Attributes", True, TAB_SELECTED_TEXT_COLOUR if not self.selected_equipment else TEXT_COLOUR),
            (self.__sects[1].x + ((self.__sects[1].w // 2) - (font.size("Attributes")[0] // 2)), (self.__sects[1].y + (self.__sects[1].h // 2)) - (font.size("Equipment")[1] // 2))
        )


class XPBar(pygame.Surface):
    """Displays the players current xp in a bar form"""
    def __init__(self) -> None:
        super().__init__((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 20), pygame.SRCALPHA)
        self.__width = WINDOW_WIDTH // 2
        self.__height = WINDOW_HEIGHT // 20

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def update(self, font: pygame.font.Font) -> None:
        """
        Updates the XPBar surface
        :param font: Font to be used to render the text
        :return: None
        """
        self.fill(XPBAR_BACKGROUND)

        # Get current XP and player level
        xp, lvl = DataLoader.player_data["xp"], DataLoader.player_data["level"]

        # XP needed per level = level * 100
        xp_needed = lvl * 100

        # Draw inner XP indicator
        pygame.draw.rect(self, XPBAR_BAR, pygame.Rect(0, 0, self.__width - (self.__width * (1 - (xp / xp_needed))), self.__height))

        # Draw outer border
        pygame.draw.rect(self, XPBAR_BORDER, pygame.Rect(0, 0, self.__width, self.__height), 15)

        # Draw text displaying level and XP
        lvl_str = f"Level {lvl}: {xp}/{xp_needed}"
        self.blit(
            font.render(lvl_str, True, TEXT_COLOUR),
            ((self.__width // 2) - (font.size(lvl_str)[0] // 2), (self.__height // 2) - (font.size(lvl_str)[1] // 2))
        )


class SkillTree(pygame.Surface):
    """Displays skill tree"""
    def __init__(self) -> None:
        self.__width = WINDOW_WIDTH // 1.25
        self.__height = WINDOW_HEIGHT // 1.25
        super().__init__((self.__width, self.__height), pygame.SRCALPHA)
        img_dims = int((WINDOW_HEIGHT / 720) * 50)
        self.__levels, self.__level_rects = self.__load_levels(DataLoader.tree_root, DataLoader.player_data["class"], img_dims)
        self.__imgs = [pygame.image.load(f"{MAIN_ASSET_PATH}{i['elem'].tag}.png") for i in self.__levels]
        self.__bw_imgs = [pygame.image.load(f"{MAIN_ASSET_PATH}{i['elem'].tag}_bw.png") for i in self.__levels]
        self.__lines = self.__get_lines(img_dims)

    def __getitem__(self, item):
        return self.__levels[item], self.__level_rects[item], self.__imgs[item]

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def __load_levels(self, tree: Element, player_class: str, img_dims: int) -> tuple:
        """
        Creates the rects for the skills to be drawn to and the correct skills for the players class
        :param tree: Xml object to extract data from
        :param player_class: The players chosen game class
        :param img_dims: Size of the images to be displayed
        :return: (levels, level_rects) to be used for drawing and other operations
        """
        # Get all levels other than the root element
        levels = [i for i in self.get_levels(None, tree, []) if i["level"] > 0]

        # Get start and end of the players class to only use their elements
        level_split_start = [pos for pos, i in enumerate(levels) if i["elem"].tag == player_class][0]
        level_split_end = [pos for pos, i in enumerate(levels) if i["elem"].tag == CLASS_NAMES[CLASS_NAMES.index(player_class) + 1]][0] if not CLASS_NAMES[CLASS_NAMES.index(player_class)] == CLASS_NAMES[-1] else None

        # Reassign levels to only include the needed elements
        levels = levels[level_split_start + 1:level_split_end]

        # Get number of subclasses to determine how many times to loop
        num_of_subclasses = sum([1 for i in levels if i["level"] == 2])

        # Get each subclass if there are 2
        if num_of_subclasses == 2:
            split_pos = [pos for pos, i in enumerate(levels) if i["elem"].tag == [j for j in levels if j["level"] == 2][1]["elem"].tag][0]
            sub_1 = levels[1:split_pos]
            sub_2 = levels[split_pos + 1:]
            levels = [sub_1, sub_2]
        else:
            levels = [levels[1:]]

        # Loop to get all data about each subclass
        level_rects = []
        for sub_num in range(len(levels)):
            # Count amount of elements on each level to determine maximum width
            num_of_levels = [i["level"] for i in levels[sub_num]]
            max_tree_width = (lambda x: x.count(max(set(x), key=x.count)))(num_of_levels) * 100

            # Get position of all rects
            rects = [
                pygame.Rect(
                    ((max_tree_width // (num_of_levels.count(i["level"]) * 2) + (img_dims if j not in [5, 6] else img_dims + (img_dims // 2))) * (num_of_levels[:j].count(i["level"]) + 1)) - (((img_dims // 2) + img_dims) - ((self.__width // 1.65) * sub_num)),
                    (self.__height // 6) * (i["level"] - 2),
                    img_dims, img_dims
                )
                for i, j in zip(levels[sub_num], range(len(num_of_levels)))
            ]
            level_rects.append(rects)

        return list(chain.from_iterable(levels)), list(chain.from_iterable(level_rects))

    def get_levels(self, parent: Element, elem: Element, arr: list, level: int=0) -> list:
        """
        Gets the objects, their level and parents in the skill tree
        :param parent: The parent element of the current element
        :param elem: The current element
        :param arr: List to hold all elements
        :param level: The depth the element is in the tree
        :return: List of all elements
        """
        # Append data about current element
        arr.append({"level": level, "parent": parent, "elem": elem})

        # For each child of the current element, get the levels below them
        for child in elem:
            self.get_levels(elem, child, arr, level + 1)

        return arr

    def __get_lines(self, img_dims: int) -> list:
        """
        Create all coords for lines in the skill tree
        :param img_dims: Dimensions of images to center lines
        :return: List of all start and end coords for the lines
        """
        # Divide img dimensions by 2 to get center point
        img_dims //= 2

        # Get relationship of each element to obtain their children
        relations = {i["elem"].tag: [j["elem"] for j in self.__levels if j["parent"] == i["elem"]] for i in self.__levels}

        # Loop through each relationship to decide whether to draw a line from them if they have children
        coords = []
        for pos, i in enumerate(relations.values()):
            for child in i:
                c_pos = [pos for pos, j in enumerate(self.__levels) if j["elem"] == child][0]
                coords.append(((self.__level_rects[pos].x + img_dims, self.__level_rects[pos].y + img_dims), (self.__level_rects[c_pos].x + img_dims, self.__level_rects[c_pos].y + img_dims)))

        return coords

    def update(self, font: pygame.font.Font, data: dict) -> None:
        """
        Updates skill tree surface each frame
        :param font: Font to use to draw text
        :param data: Data to determine which rect was collided
        :return: None
        """
        self.fill(SKILLTREE_BACKGROUND)

        # Get skill points text to be drawn
        text = f"Unused SP: {DataLoader.player_data['unused_sp']}"

        # Draw border of surface
        pygame.draw.rect(self, SKILLTREE_BORDER, pygame.Rect(0, 0, self.__width, self.__height), 5)

        # Draw skill point border
        pygame.draw.rect(
            self, SKILLTREE_SP_BORDER,
            pygame.Rect(
                (self.__width // 2) - (font.size(text)[0] // 2),
                self.__height - font.size(text)[1],
                font.size(text)[0],
                font.size(text)[1]
            )
        )

        # Draw skill point text
        self.blit(
            font.render(text, True, TEXT_COLOUR),
            ((self.__width // 2) - (font.size(text)[0] // 2), self.__height - font.size(text)[1])
        )

        # Draw connecting lines between each tree element
        for line in self.__lines:
            pygame.draw.aaline(self, (255, 255, 255), (line[0][0], line[0][1]), (line[1][0], line[1][1]))

        # Draw skill image
        for pos, rect in enumerate(self.__level_rects):
            # Draw border around image if the mouse is hovered over it
            if data is not None:
                if data["st_pos"] == rect:
                    pygame.draw.rect(self, (255, 255, 255), rect, 5)
            self.blit(self.__imgs[pos] if self.__levels[pos]["elem"].tag in DataLoader.player_data["skills"] else self.__bw_imgs[pos], rect)


class ItemDropDisplay(pygame.Surface):
    """Displays the item which was recently picked up by the player"""
    def __init__(self) -> None:
        super().__init__((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 1.5), pygame.SRCALPHA)
        self.__width = WINDOW_WIDTH // 2
        self.__height = WINDOW_HEIGHT // 2
        self.__items = []
        self.__times = []

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def add_item(self, item: tuple) -> None:
        """
        Adds item to the items list to be displayed
        :param item: Tuple of name of item picked up and pygame.image of item
        :return: None
        """
        self.__items.insert(0, item)
        self.__times.insert(0, time())

    def update(self, font: pygame.font.Font) -> None:
        """
        Updates ItemDropDisplay surface each frame
        :param font: Font in which the text should be written in
        :return: None
        """
        self.fill(ITEM_DROP_DISPLAY_BACKGROUND)

        for pos, item in enumerate(self.__items):
            # Background rect with the rarity of the item as its colour
            pygame.draw.rect(
                self, DataLoader.rarities[DataLoader.possible_items[item[0]]["rarity"]],
                pygame.Rect(
                    self.width - item[1].get_width(),
                    (pos * item[1].get_height()),
                    item[1].get_width(),
                    item[1].get_height()
                )
            )

            # Dimensions which the text will take up
            str_width, str_height = font.size(item[0])

            # Draw item image
            self.blit(item[1], (self.width - item[1].get_width(), (pos * item[1].get_height())))

            # Draw item name text
            self.blit(
                font.render(item[0], True, TEXT_COLOUR),
                (self.width - item[1].get_width() - str_width, (pos * item[1].get_height()) + (str_height // 2))
            )

            if time() - self.__times[pos] >= 3:
                del self.__items[pos]
                del self.__times[pos]


class Menu(pygame.Surface):
    def __init__(self, x: int, y: int, buttons: list) -> None:
        super().__init__((MENU_WIDTH, MENU_HEIGHT), pygame.SRCALPHA)
        self.__x = x
        self.__y = y
        self.__width = MENU_WIDTH
        self.__height = MENU_HEIGHT
        self.__buttons = buttons

        self.__button_pos = [
            pygame.Rect(
                MENU_MARGIN_X,
                ((self.__height / len(self.__buttons)) * i) + MENU_MARGIN_Y,
                self.__width - (MENU_MARGIN_X * 2),
                (self.__height / len(self.__buttons)) - (MENU_MARGIN_Y * 2)
            ) for i in range(len(self.__buttons))
        ]

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def manual_press(self, button_name: str) -> None:
        """
        Calls the function of the button with the specified name
        :param button_name: Name of the button to press
        :return: None
        """
        for b in self.__buttons:
            if b[0] == button_name:
                b[1]()

    def check_pressed(self, mx: int, my: int, flag: int=1) -> Optional[pygame.Rect]:
        """
        Checks whether any of the buttons were pressed and either: execute the function or return the rect
        :param mx: mouse x position
        :param my: mouse y position
        :param flag: determines whether the function is called(flag=1) or the rect is returned(flag=any int except 1)
        :return: None or the button rect
        """
        for button, button_pos in zip(self.__buttons, self.__button_pos):
            if pygame.Rect(button_pos.x + self.__x, button_pos.y + self.__y, button_pos.w, button_pos.h).collidepoint(mx, my):
                # button is a tuple in the form (text, func)
                if flag == 1:
                    button[1]()
                else:
                    return button_pos

    def update(self, font: pygame.font.Font, mx: int, my: int) -> None:
        """
        Draws the buttons and corresponding text to the Menu surface
        :param font: font to draw the text with
        :param mx: mouse x position
        :param my: mouse y position
        :return: None
        """
        self.fill(MENU_BACKGROUND_COLOUR)

        # Check if any buttons are being hovered over
        focused_rect = self.check_pressed(mx, my, 2)

        # Loop through buttons to draw them
        for b, bp in zip(self.__buttons, self.__button_pos):
            pygame.draw.rect(self, MENU_BUTTON_COLOUR, bp)

            # Draw border around the hovered over button
            if bp == focused_rect:
                pygame.draw.rect(self, MENU_SELECTED, bp, 4)

            # Draw the name of the button
            txt = font.render(b[0], True, TEXT_COLOUR)
            txt_size = font.size(b[0])
            self.blit(txt, ((self.__width // 2) - (txt_size[0] // 2), bp.y + (bp.h // 2) - (txt_size[1] // 2)))


class SelectMenu(pygame.Surface):
    def __init__(self, x: int, y: int, buttons: list) -> None:
        super().__init__((SELECT_MENU_WIDTH, SELECT_MENU_HEIGHT), pygame.SRCALPHA)
        self.__x = x
        self.__y = y
        self.__width = SELECT_MENU_WIDTH
        self.__height = SELECT_MENU_HEIGHT
        n = 5
        self.__buttons = [buttons[i: i + n] for i in range(0, len(buttons), n)]
        self.__left_button = pygame.Rect(0, self.__height - SELECT_MENU_MARGIN_Y, SELECT_MENU_MARGIN_X, SELECT_MENU_MARGIN_Y)
        self.__right_button = pygame.Rect(self.__width - SELECT_MENU_MARGIN_X, self.__height - SELECT_MENU_MARGIN_Y, SELECT_MENU_MARGIN_X, SELECT_MENU_MARGIN_Y)

        self.__button_pos = [
            pygame.Rect(
                SELECT_MENU_MARGIN_X,
                ((self.__height / n) * i) + SELECT_MENU_MARGIN_Y,
                self.__width - (SELECT_MENU_MARGIN_X * 2),
                (self.__height / n) - (SELECT_MENU_MARGIN_Y * 2)
            ) for i in range(n)
        ]
        self.__current_page = 0

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def current_page(self):
        return self.__current_page

    @current_page.setter
    def current_page(self, value: int):
        self.__current_page = value if 0 <= value < len(self.__buttons) else self.__current_page

    def check_pressed(self, mx: int, my: int, flag: int=1) -> Optional[pygame.Rect]:
        """
        Checks whether any of the buttons were pressed and either: execute the function or return the rect
        :param mx: mouse x position
        :param my: mouse y position
        :param flag: determines whether the function is called(flag=1) or the rect is returned(flag=any int except 1)
        :return: None or the button rect
        """
        for button, button_pos in zip(self.__buttons[self.__current_page], self.__button_pos):
            if pygame.Rect(button_pos.x + self.__x, button_pos.y + self.__y, button_pos.w, button_pos.h).collidepoint(mx, my):
                # button is a tuple in the form ((text, text), func) or ((text, text, text), func)
                if flag == 1:
                    if len(button[0]) > 2:
                        button[1](button[0][0])
                    else:
                        button[1]()
                else:
                    return button_pos

    def update(self, font: pygame.font.Font, mx: int, my: int, chr_sel: str=None) -> None:
        """
        Draws all buttons and their text
        :param font: font to draw the text with
        :param mx: mouse x position
        :param my: mouse y position
        :param chr_sel: name of the character selected, if one is selected
        :return: None
        """
        self.fill(SELECT_MENU_BACKGROUND_COLOUR)

        # Check if any buttons are being hovered over
        focused_rect = self.check_pressed(mx, my, 2)

        # Draw the left and right button rects
        pygame.draw.rect(self, SELECT_MENU_BUTTON_COLOUR, self.__left_button)
        pygame.draw.rect(self, SELECT_MENU_BUTTON_COLOUR, self.__right_button)

        # Draw left and right button text
        left_arrow = font.render("<-", True, TEXT_COLOUR)
        right_arrow = font.render("->", True, TEXT_COLOUR)
        self.blit(left_arrow, (self.__left_button.x, self.__left_button.y))
        self.blit(right_arrow, (self.__right_button.x, self.__right_button.y))

        # Loop through buttons to draw them
        for button, button_pos in zip(self.__buttons[self.__current_page], self.__button_pos):
            # Draw button rect
            pygame.draw.rect(self, SELECT_MENU_BUTTON_COLOUR, button_pos)

            # if a character is selected, draw a selected border around the button
            if chr_sel is not None:
                if chr_sel == button[0][0]:
                    pygame.draw.rect(self, SELECT_MENU_CHARACTER_SELECTED, button_pos, 4)

            # Draw border around the hovered over button
            if button_pos == focused_rect:
                pygame.draw.rect(self, SELECT_MENU_SELECTED, button_pos, 4)

            # Draw all text corresponding to the button
            main_txt = font.render(button[0][0], True, TEXT_COLOUR)
            second_txt = font.render(str(button[0][1]), True, TEXT_COLOUR)
            self.blit(main_txt, (button_pos.x, button_pos.y))
            self.blit(second_txt, (button_pos.x + button_pos.w - font.size(str(button[0][1]))[0], button_pos.y))
            if len(button[0]) > 2:
                third_txt = font.render(button[0][2], True, TEXT_COLOUR)
                self.blit(third_txt, (button_pos.x, button_pos.y + button_pos.h - font.size(button[0][2])[1]))


class CharacterCreator(pygame.Surface):
    def __init__(self) -> None:
        super().__init__((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), pygame.SRCALPHA)
        self.__width = WINDOW_WIDTH // 2
        self.__height = WINDOW_HEIGHT // 2
        self.__x = (WINDOW_WIDTH // 2) - (self.__width // 2)
        self.__y = (WINDOW_HEIGHT // 2) - (self.__height // 2)
        margin_x = 20
        margin_y = 40
        self.__name = ""
        w = (self.__width - (margin_x * 5)) // 4
        h = (self.__height - (margin_y * 4)) // 3
        self.__name_rect = pygame.Rect(margin_x, margin_y, self.__width - (margin_x * 2), h)
        self.__confirm_rect = pygame.Rect((margin_x * 2) + w, (margin_y * 3) + (h * 2), (w * 2) + margin_x, h)
        self.__class_rects = [pygame.Rect((margin_x * (i + 1)) + (w * i), (margin_y * 2) + h, w, h) for i in range(4)]
        self.__selected_class = None
        self.__confirm_pressed = False

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def confirm_pressed(self):
        return self.__confirm_pressed

    @property
    def selected_class(self):
        return self.__selected_class

    @property
    def name(self):
        return self.__name

    def add_char(self, char: str) -> None:
        """
        Adds character to the text box
        :param char: The character to add
        :return: None
        """
        if len(self.__name) < 21:
            self.__name += char

    def remove_char(self) -> None:
        """
        Remove most recent character from the string
        :return: None
        """
        if len(self.__name) > 0:
            self.__name = self.__name[:-1]

    def check_pressed(self, mx: int, my: int) -> None:
        """
        Check if the confirm button has been pressed
        :param mx: Mouse x position
        :param my: Mouse y position
        :return: None
        """
        mx, my = mx - self.__x, my - self.__y
        for pos, cr in enumerate(self.__class_rects):
            if cr.collidepoint(mx, my):
                self.__selected_class = CLASS_NAMES[pos]

        if self.__confirm_rect.collidepoint(mx, my) and self.__selected_class is not None and len(self.__name) > 0:
            self.__confirm_pressed = True

    def update(self, font, mx: int, my: int) -> None:
        """
        Update the CharacterCreator surface
        :param font: Font to draw the text with
        :param mx: Mouse x position
        :param my: Mouse y position
        :return: None
        """
        self.fill((60, 60, 60, 60))
        mx, my = mx - self.__x, my - self.__y
        pygame.draw.rect(self, (0, 0, 0), self.__name_rect)
        pygame.draw.rect(self, (255, 255, 255), self.__name_rect, 5)
        self.blit(
            font.render(self.__name, True, (255, 255, 255)),
            (
                self.__name_rect.x - (font.size(self.__name)[0] // 2) + (self.__name_rect.w // 2),
                self.__name_rect.y - (font.size(self.__name)[1] // 2) + (self.__name_rect.h // 2)
            )
        )
        pygame.draw.rect(self, (255, 128, 0), self.__confirm_rect)
        if self.__confirm_rect.collidepoint(mx, my):
            pygame.draw.rect(self, (255, 255, 255), self.__confirm_rect, 5)
        self.blit(
            font.render("Confirm", True, (255, 255, 255)),
            (
                self.__confirm_rect.x - (font.size("Confirm")[0] // 2) + (self.__confirm_rect.w // 2),
                self.__confirm_rect.y - (font.size("Confirm")[1] // 2) + (self.__confirm_rect.h // 2)
            )
        )
        for pos, c in enumerate(self.__class_rects):
            pygame.draw.rect(self, (255, 128, 0), c)
            if c.collidepoint(mx, my):
                pygame.draw.rect(self, (255, 255, 255), c, 5)
            if CLASS_NAMES[pos] == self.__selected_class:
                pygame.draw.rect(self, (0, 255, 0), c, 5)
            x = c.x - (font.size(CLASS_NAMES[pos])[0] // 2) + (c.w // 2)
            y = c.y - (font.size(CLASS_NAMES[pos])[1] // 2) + (c.h // 2)
            txt = font.render(CLASS_NAMES[pos], True, (255, 255, 255))
            self.blit(txt, (x, y))


class MessageBox(pygame.Surface):
    def __init__(self, txt: str, background: tuple) -> None:
        self.__width = WINDOW_WIDTH // 1.1
        self.__height = WINDOW_HEIGHT // 6
        super().__init__((self.__width, self.__height))
        self.__x = (WINDOW_WIDTH // 2) - (self.__width // 2)
        self.__y = (WINDOW_HEIGHT // 2) - (self.__height // 2)
        self.__txt = txt
        margin_x = 10
        margin_y = 10
        self.__inner_box = pygame.Rect(margin_x, margin_y, self.__width - margin_x*2, self.__height - margin_y*2)
        self.__background = background
        button_width = self.__width // 10
        button_height = self.__height // 4
        self.__button = pygame.Rect(
            (self.__width // 2) - (button_width // 2),
            self.__height - button_height - margin_y*2,
            button_width, button_height
        )

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def check_pressed(self, mx: int, my: int) -> bool:
        """
        Checks if the exit button has been pressed
        :param mx: Mouse x position
        :param my: Mouse y position
        :return: True if pressed else False
        """
        if self.__button.collidepoint(mx - self.__x, my - self.__y):
            return True
        return False

    def update(self, font: pygame.font.Font) -> None:
        """
        Updates the MessageBox surface
        :param font: Font to draw the text with
        :return: None
        """
        self.fill((60, 60, 60))
        pygame.draw.rect(self, self.__background, self.__inner_box)
        pygame.draw.rect(self, (255, 255, 255), self.__button)
        txt = font.render(self.__txt, True, (255, 255, 255))
        self.blit(
            txt,
            ((self.__width // 2) - (font.size(self.__txt)[0] // 2), (self.__height // 2) - (font.size(self.__txt)[1] // 2))
        )
        button_txt = font.render("EXIT", True, (0, 0, 0))
        self.blit(
            button_txt,
            ((self.__width // 2) - (font.size("EXIT")[0] // 2), (self.__button.y + (self.__button.h // 2)) - (font.size("EXIT")[1] // 2))
        )


if __name__ == '__main__':
    pass
