import json
import inspect
from constants import *
from xml.etree import ElementTree
from PIL import Image
from os import listdir, mkdir
from os.path import isfile, join, isdir


class DataLoader:
    """Used to handle files"""
    player_name = ""
    rarities = json.load(open(RARITIES_PATH))["rarities"]
    possible_items = json.load(open(ITEMS_PATH))
    loot_table = json.load(open(LOOT_TABLE_PATH))
    tree_root = ElementTree.parse(SKILL_TREE_PATH).getroot()
    all_player_data = json.load(open(PLAYER_DATA_PATH))
    game_level = 1
    host_name = None
    player_data = None
    __funcs = None

    def __init__(self) -> None:
        DataLoader.player_data = json.load(open(PLAYER_DATA_PATH))[DataLoader.player_name]
        DataLoader.__funcs = {i[0]: i[1] for i in inspect.getmembers(self, inspect.ismethod) if not i[0].startswith("__")}
        self.__resize_images()

    @staticmethod
    def store_maze(maze: str) -> None:
        """
        Stores the maze created by maze_creator.py
        :param maze: maze formatted from 2d list to str
        :return: None
        """
        with open("data/maze.txt", "w") as f:
            f.write(maze)

    @staticmethod
    def create_new_player(name: str, class_: str) -> None:
        """
        Creates a new player character in the player_data.json file
        :return: None
        """
        with open(PLAYER_DATA_PATH) as f:
            file = json.load(f)

        file[name] = {
            "armor": {"head": "basic_head", "chest": "basic_chest", "legs": "basic_legs", "feet": "basic_feet"},
            "hotbar": ["axe", None, None, None, None],
            "inventory": [None] * 20,
            "attributes": {"health": 1, "mana": 1, "strength": 1, "defense": 1},
            "skills": {},
            "level": 1,
            "xp": 0,
            "unused_sp": 0,
            "coins": 0,
            "class": class_
        }

        with open(PLAYER_DATA_PATH, "w") as f:
            json.dump(file, f, indent=4)

        DataLoader.all_player_data = json.load(open(PLAYER_DATA_PATH))

    @staticmethod
    def change_file(func_name: str, *args) -> None:
        """
        Changes the player data file
        Uses __funcs to call the correct function and passes in args

        e.g __increment_attr function:

        |     A section of the __funcs dict  |  String needs to be concat |
        |                                    |    because it is private   |

        {"_DataLoader__increment_attr": <...>}["_DataLoader__" + func_name](file, *args)
                                          ^                                          ^
                                    The func obj                              (attr, amount)

        :param func_name: The function name to be called
        :param args: Any arguments that function requires
        :return: None
        """
        with open(PLAYER_DATA_PATH) as f:
            file = json.load(f)

        # Call the selected function
        file = DataLoader.__funcs["_DataLoader__" + func_name](file, *args)
        DataLoader.player_data = file[DataLoader.player_name]

        with open(PLAYER_DATA_PATH, "w") as f:
            json.dump(file, f, indent=4)

    @staticmethod
    def __resize_images() -> None:
        """
        Resizes all asset images to fit the resolution of the window
        :return: None
        """
        new_path = f"{BASE_PATH}/assets/{WINDOW_WIDTH}x{WINDOW_HEIGHT}/"
        if not isdir(new_path):
            mkdir(new_path)

            for size, folders in ASSET_DIRECTORY_SIZES.items():
                for folder_from in folders:
                    files = [f for f in listdir(BASE_PATH + folder_from) if isfile(join(BASE_PATH + folder_from, f))]

                    if isinstance(size, int):
                        height = int((WINDOW_HEIGHT / 720) * size)
                        width = height
                        for file in files:
                            im = Image.open(BASE_PATH + folder_from + file)
                            resized = im.resize((width, height))
                            resized.save(new_path + file)
                            print(f"Saved {file}")

                    # Entities dont get resized
                    elif size == "DONT_RESIZE":
                        for file in files:
                            im = Image.open(BASE_PATH + folder_from + file)
                            im.save(new_path + file)
                            print(f"Saved {file}")

    @staticmethod
    def get_next_open_inv_slot() -> int:
        """
        Get next open slot in inventory if there is one (open slot indicated by None value), else return None
        :return: Position in player_data['inventory'] list of next open slot
        """
        return None if None not in DataLoader.player_data["inventory"] else DataLoader.player_data["inventory"].index(None)

    @staticmethod
    def get_player_defense() -> int:
        """
        Get total defense of the player by adding the total armor defense to the attribute defense
        :return: Total defense
        """
        return DataLoader.player_data["attributes"]["defense"] + sum(
            [DataLoader.possible_items[i]["defense"] for i in DataLoader.player_data["armor"].values()]
        )

    def __increment_attr(self, file: dict, attr: str, amount: int) -> dict:
        """
        Increments the player attributes
        :param file: Dict to update
        :param attr: The attribute to be incremented, e.g 'health'
        :param amount: The amount of points to be added
        :return: Updated file
        """
        file[DataLoader.player_name]["attributes"][attr] += amount
        return file

    def __increment_sp(self, file: dict, amount: int) -> dict:
        """
        Increments the unused_sp value
        :param file: Dict to update
        :param amount: The amount to increment the value by
        :return: Updated file
        """
        file[DataLoader.player_name]["unused_sp"] += amount
        return file

    def __add_to_inv(self, file: dict, item: str, pos: int) -> dict:
        """
        Adds item to the players inventory
        :param file: Dict to update
        :param item: The item to be added to the inventory
        :param pos: The position in the list to add the item
        :return: Updated file
        """
        item = None if item == "no_item" else item
        file[DataLoader.player_name]["inventory"].insert(pos, item)
        return file

    def __remove_from_inv(self, file: dict, pos: int) -> dict:
        """
        Removes item from the players inventory
        :param file: Dict to update
        :param pos: The position in the inventory list to delete
        :return: Updated file
        """
        del file[DataLoader.player_name]["inventory"][pos]
        return file

    def __add_to_hotbar(self, file: dict, item: str, pos: int) -> dict:
        """
        Adds item to the hotbar
        :param file: Dict to update
        :param item: The item to add to the hotbar
        :param pos: The position in the hotbar list
        :return: Updated file
        """
        item = None if item == "no_item" else item
        file[DataLoader.player_name]["hotbar"].insert(pos, item)
        return file

    def __remove_from_hotbar(self, file: dict, pos: int) -> dict:
        """
        Removes item from the hotbar
        :param file: Dict to update
        :param pos: The position in the hotbar list
        :return: Updated file
        """
        del file[DataLoader.player_name]["hotbar"][pos]
        return file

    def __add_to_armor(self, file: dict, piece: str, name: str) -> dict:
        """
        Add armor piece to armor dict
        :param file: Dict to update
        :param piece: The armor piece to update
        :param name: The name of the new armor piece
        :return: Updated file
        """
        file[DataLoader.player_name]["armor"][piece] = name
        return file

    def __remove_from_armor(self, file: dict, piece: str) -> dict:
        """
        Remove armor piece from armor dict
        :param file: Dict to update
        :param piece: The armor piece to update
        :return: Updated file
        """
        file[DataLoader.player_name]["armor"][piece] = None
        return file

    def __add_xp(self, file: dict, amount: int) -> dict:
        """
        Adds XP to the player
        :param file: Dict to update
        :param amount: Amount of xp to add
        :return: Updated file
        """
        file[DataLoader.player_name]["xp"] += amount
        return file

    def __reset_xp(self, file: dict) -> dict:
        """
        Resets player xp when leveled up
        :param file: Dict to update
        :return: Updated file
        """
        file[DataLoader.player_name]["xp"] = 0
        return file

    def __add_level(self, file: dict) -> dict:
        """
        Adds 1 level to the player
        :param file: Dict to update
        :return: Updated file
        """
        file[DataLoader.player_name]["level"] += 1
        return file

    def __add_skill(self, file: dict, skill: str) -> dict:
        """
        Either add or increment a skill in the skill tree
        :param file: Dict to update
        :param skill: Name of skill to add
        :return: Updated file
        """
        if file[DataLoader.player_name]["skills"].get(skill):
            file[DataLoader.player_name]["skills"][skill] += 1
        else:
            file[DataLoader.player_name]["skills"][skill] = 1
        return file


if __name__ == '__main__':
    pass
