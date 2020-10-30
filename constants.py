from os import getcwd

# Colours
TEXT_COLOUR = (255, 255, 255)
COIN_TEXT_COLOUR = (255, 255, 0)
TAB_SELECTED_TEXT_COLOUR = (0, 0, 0)

HOTBAR_BACKGROUND = (20, 20, 20, 150)

INV_BACKGROUND = (20, 20, 20, 150)
INV_SELECTED = (255, 255, 255)

INSPECTOR_BACKGROUND = (20, 20, 20, 150)

EQUIPMENT_BACKGROUND = (20, 20, 20, 150)
EQUIPMENT_BORDER = (255, 128, 0)
EQUIPMENT_SELECTED = (255, 255, 255)

HEALTHBAR_BACKGROUND_COLOUR = (255, 0, 0)
HEALTHBAR_TEXT_COLOUR = (255, 0, 0)

MANABAR_BACKGROUND_COLOUR = (0, 0, 255)
MANABAR_TEXT_COLOUR = (0, 0, 255)

ATTRIBURES_BACKGROUND = (20, 20, 20, 150)
ATTRIBURES_BORDER = (255, 128, 0)
ATTRIBURES_SP_BORDER = (100, 0, 192)

TAB_BACKGROUND = (20, 20, 20, 150)
TAB_BORDER = (255, 128, 0)

XPBAR_BACKGROUND = (20, 20, 20, 150)
XPBAR_BAR = (100, 0, 192)
XPBAR_BORDER = (20, 20, 20)

SKILLTREE_BACKGROUND = (20, 20, 20, 150)
SKILLTREE_BORDER = (255, 128, 0)
SKILLTREE_SP_BORDER = (100, 0, 192)

ITEM_DROP_BACKGROUND = (0, 0, 0, 0)

ITEM_DROP_DISPLAY_BACKGROUND = (0, 0, 0, 0)

BEZIER_POINT_COLOUR = (0, 0, 255)

MENU_BACKGROUND_COLOUR = (60, 60, 60, 60)
MENU_BUTTON_COLOUR = (255, 128, 0)
MENU_SELECTED = (255, 255, 255)

BOARD_BACKGROUND = (0, 0, 0)
WALL_COLOUR = (160, 82, 45)
DOOR_COLOUR = (160, 82, 45)

SELECT_MENU_BACKGROUND_COLOUR = (60, 60, 60, 60)
SELECT_MENU_BUTTON_COLOUR = (255, 128, 0)
SELECT_MENU_SELECTED = (255, 255, 255)

# DIMENSIONS
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

ENTITY_INFO = {
    "player": (40, 40),
    "small": (21, 21, 10),
    "medium": (40, 40, 30),
    "large": (60, 60, 50)
}

BOARD_WIDTH = 2050
BOARD_HEIGHT = 2050

WALL_VERTICAL_WIDTH = 20
WALL_HORIZONTAL_WIDTH = 400
WALL_VERTICAL_HEIGHT = 400
WALL_HORIZONTAL_HEIGHT = 20

CELL_WIDTH = 380
CELL_HEIGHT = 380

DOOR_VERTICAL_WIDTH = 20
DOOR_HORIZONTAL_WIDTH = 200
DOOR_VERTICAL_HEIGHT = 200
DOOR_HORIZONTAL_HEIGHT = 20

ITEM_DROP_WIDTH = 50
ITEM_DROP_HEIGHT = 50

MAX_MELEE_SWING_WIDTH = 200
MAX_MELEE_SWING_HEIGHT = 200

MENU_WIDTH = 300
MENU_HEIGHT = 500
MENU_MARGIN_X = 20
MENU_MARGIN_Y = 20

SELECT_MENU_WIDTH = 800
SELECT_MENU_HEIGHT = 600
SELECT_MENU_MARGIN_X = 50
SELECT_MENU_MARGIN_Y = 20

# Misc Values
MAX_BULLET_SPEED = 19
PLAYER_DAMAGE_COOLDOWN = 5
ENEMY_DAMAGE_COOLDOWN = 5
PLAYER_MV_AMOUNT = 10
GNS_IP = "192.168.1.103"
GNS_PORT = 50000

# File paths
MAZE_PATH = "data/maze.txt"
RARITIES_PATH = "data/colours.json"
ITEMS_PATH = "data/items.json"
PLAYER_DATA_PATH = "data/player_data.json"
SKILL_TREE_PATH = "data/skill_tree.xml"
LOOT_TABLE_PATH = "data/loot_table.json"

# Player class names
CLASS_NAMES = ["mage", "warrior", "archer", "looter"]

# Item drop pickup frame amounts
ITEM_DROP_FRAME_AMOUNT = {
    "bronze": 26,
    "silver": 26,
    "gold": 26,
    "diamond": 26
}

# Directories
BASE_PATH = getcwd().replace("\\", "/") + "/"

MAIN_ASSET_PATH = f"assets/{WINDOW_WIDTH}x{WINDOW_HEIGHT}/"

ASSET_DIRECTORY_SIZES = {
    50: [
        "assets/archer/deadeye/",
        "assets/archer/fire_thrower/",
        "assets/looter/",
        "assets/mage/fire/",
        "assets/mage/ice/",
        "assets/warrior/berserker/",
        "assets/warrior/tank/",
        "assets/items/"
    ],
    "DONT_RESIZE": [
        "assets/entities/",
        "assets/animation/bronze/",
        "assets/animation/silver/",
        "assets/animation/gold/",
        "assets/animation/diamond/"
    ],
    25: ["assets/ui/"]
}
