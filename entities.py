import pygame
import math
from constants import *
from data_loader import DataLoader
from a_star import AStar
from board import Board
from secrets import randbelow
from items import Item
from utils import colour_lerp
from random import randint
from dataclasses import dataclass
from math import sin, cos


class Player(pygame.Surface):
    def __init__(self):
        self.__width = ENTITY_INFO["player"][0]
        self.__height = ENTITY_INFO["player"][1]
        super().__init__((self.__width * 2, self.__height * 2), pygame.SRCALPHA)
        self.__img = pygame.image.load(f"assets/{WINDOW_WIDTH}x{WINDOW_HEIGHT}/player.png")
        self.x, self.y = 200, 200
        self.__max_health, self.__health = None, None
        self.__max_mana, self.__mana = None, None
        self.reset_health_and_mana()
        self.melee_cooldown = 0
        self.mv_amount = PLAYER_MV_AMOUNT
        self.__damage_cooldown = 0

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def health(self):
        return self.__health

    @property
    def mana(self):
        return self.__mana

    @health.setter
    def health(self, value):
        # If the new health value < current health then damage has been done
        if value < self.__health:
            if self.__damage_cooldown == 0:
                damage = (self.__health - value) - DataLoader.get_player_defense()
                self.__health -= damage if damage > 0 else 0
                self.__damage_cooldown = PLAYER_DAMAGE_COOLDOWN
        else:
            self.__health = value

    @mana.setter
    def mana(self, value):
        pass

    def reset_health_and_mana(self):
        self.__max_health = (100 * DataLoader.player_data["level"]) + (DataLoader.player_data["attributes"]["health"] * 20)
        self.__max_mana = (50 * DataLoader.player_data["level"]) + (DataLoader.player_data["attributes"]["mana"] * 10)
        self.__health = self.__max_health
        self.__mana = self.__max_mana

    def reset_level(self):
        if DataLoader.player_data["xp"] >= DataLoader.player_data["level"] * 100:
            DataLoader.change_file("reset_xp")
            DataLoader.change_file("add_level")

    def update(self, mx, my):
        self.fill((0, 0, 0, 0))
        degrees = math.degrees(math.atan2((self.x + self.__width) - mx, (self.y + self.__height) - my))
        rotated_img = pygame.transform.rotate(self.__img, degrees)
        self.blit(rotated_img, (self.__width // 2, self.__height // 2))

        # Damage cooldown
        if self.__damage_cooldown > 0:
            self.__damage_cooldown -= 1

        # Check if the player has leveled up
        self.reset_level()


class Enemy(pygame.Surface):
    """Base enemy class"""
    def __init__(self, x, y, size):
        self.__width = ENTITY_INFO[size][0]
        self.__height = ENTITY_INFO[size][1]
        super().__init__((self.__width * 2, self.__height * 2), pygame.SRCALPHA)
        self.x, self.y = x, y
        self.__max_health = ENTITY_INFO[size][2]
        self.__health = self.__max_health
        self.__img = pygame.image.load(f"assets/{WINDOW_WIDTH}x{WINDOW_HEIGHT}/{size}.png")
        self.__board = None
        self.__speed = 5
        self.__is_moving = False
        self.__size = size
        self.__colour_grad = [i for i in colour_lerp((255, 9, 0), (0, 255, 0), self.__max_health)]
        self.__damage_cooldown = 0

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def health(self):
        return self.__health

    @health.setter
    def health(self, value):
        if self.__damage_cooldown == 0:
            self.__health = value
            self.__damage_cooldown = ENEMY_DAMAGE_COOLDOWN

    def __goto(self, prev_cell: tuple, new_cell: tuple) -> tuple:
        """
        Gets x and y move amounts to move enemies to next cell
        :param prev_cell: Cell the enemy is currently in
        :param new_cell: Cell the enemy will move to
        :return: x and y move amounts
        """
        # Direction factors
        dirs = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}

        x_amount, y_amount = 0, 0
        for dir_ in dirs.values():
            if prev_cell[0] + dir_[0] == new_cell[0] and prev_cell[1] + dir_[1] == new_cell[1]:
                x_amount = self.__speed * dir_[0]
                y_amount = self.__speed * dir_[1]
        return x_amount, y_amount

    def __move(self, player_x: int, player_y: int) -> None:
        """
        Uses the equation:
        (x, y) = (x1 + k(x2 - x1), y1 + k(y2 - y1))

        where (x1, y1) is the start point,
              (x2, y2) is the endpoint,
              k is the fraction of the line you want to divide

        This subdivides the line to calculate the next coordinate to move the enemy to depending on the speed
        :param player_x: Players x coordinate
        :param player_y: Players y coordinate
        :return: None
        """
        # Calculate Euclidean distance from current pos to player pos
        dist = math.sqrt((player_x - self.x) ** 2 + (player_y - self.y) ** 2)

        # Calculate the number of times the line can be divided by the speed
        num_of_divisions = abs(dist / (1 - self.__speed))

        # Sets new coords using equation
        self.x = self.x + ((1 / num_of_divisions) * (player_x - self.x))
        self.y = self.y + ((1 / num_of_divisions) * (player_y - self.y))

    @staticmethod
    def _get_path(start_x, start_y, end_x, end_y, cell_table):
        # Columns and rows set to 0 because they are reassigned when the maze file is read
        a = list(reversed(AStar(0, 0).solve((start_y, start_x), (end_y, end_x))[0]))

        # Reverse keys and values
        cell_table = {v: k for k, v in cell_table.items()}

        # Get the acc cell positions of path
        return [cell_table[(a[i].x, a[i].y)] for i in range(0, len(a), 2)]

    def __find_path(self, start_x: int, start_y: int, end_x: int, end_y: int, cell_table: dict, player: Player) -> tuple:
        """
        Finds path for enemy to move to player
        :param start_x: Current x coord
        :param start_y: Current y coord
        :param end_x: Player x coord
        :param end_y: Player y coord
        :param cell_table: Dict of cell pos and file pos
        :param player: Player obj
        :return: x and y move amounts
        """
        # Get path
        path = self._get_path(start_x, start_y, end_x, end_y, cell_table)

        # If the enemy isn't in the cell the player is in then move
        if len(path) > 1:
            self.__is_moving = True
            return self.__goto(path[0], path[1])

        # If enemy is in the same cell as the player
        elif len(path) == 1:
            self.__is_moving = True
            self.__move(player.x, player.y)

        else:
            self.__is_moving = False

    def update(self, closest_player: Player, cur_pos: tuple, player_pos: tuple, cell_table: dict, board: Board):
        self.fill((0, 0, 0, 0))
        self.__board = board
        if self.__size != "large":
            mv_info = self.__find_path(*cur_pos, *player_pos, cell_table, closest_player)

            if self.__is_moving and mv_info is not None:
                self.x += mv_info[0]
                self.y += mv_info[1]

        # Rotates enemy image towards player
        degrees = math.degrees(math.atan2(self.x - closest_player.x, self.y - closest_player.y))
        rotated_img = pygame.transform.rotate(self.__img, degrees)
        self.blit(rotated_img, (self.__width // 2, self.__height // 2))

        # Draw health indicator
        pygame.draw.rect(self, self.__colour_grad[self.__health - 1], (0, 0, (self.__width * 2) * (self.__health / self.__max_health), self.__height // 10))

        # Damage cooldown
        if self.__damage_cooldown > 0:
            self.__damage_cooldown -= 1

    def kill(self) -> tuple:
        """
        Called when enemy is dead
        :return: Tuple of (x, y, item, xp)
        """
        # Gets random number with bounds [1, 101)
        rng = randbelow(100) + 1
        for loot, chance in sorted(DataLoader.loot_table[self.__size]["drops"].items(), key=lambda x: x[1]):
            if rng <= chance:
                return self.x, self.y, Item(loot), DataLoader.loot_table[self.__size]["xp"]


class SmallEnemy(Enemy):
    def __init__(self, x, y, origin=0):
        super().__init__(x, y, "small")
        self.__speed = 10
        self.origin = origin

    @classmethod
    def from_large_enemy(cls, parent):
        return cls(parent.x + parent.width, parent.y + parent.height, 1)


class MediumEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "medium")
        self.__speed = 4
        self.bullets = []

    def update(self, closest_player: Player, cur_pos: tuple, player_pos: tuple, cell_table: dict, board: Board):
        # Call superclass update() function for movement
        super().update(closest_player, cur_pos, player_pos, cell_table, board)

        # Attack behaviour
        if randint(1, 10) == 10:
            self.bullets.append(
                Bullet(
                    self.x + self.width - board.x, self.y + self.height - board.y,
                    closest_player.x + closest_player.width - board.x, closest_player.y + closest_player.height - board.y,
                    DataLoader.possible_items["medium_enemy_weapon"]
                )
            )


class LargeEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, "large")
        self.l_enemy_pos = []
        self.__prev_cell = []
        self.__cur_cell = []
        self.spawned_enemies = []
        self.bezier_points = []

    def update(self, closest_player: Player, cur_pos: tuple, player_pos: tuple, cell_table: dict, board: Board):
        # Stop enemy from moving
        self.__is_moving = False

        # Get path to player
        path = self._get_path(*cur_pos, *player_pos, cell_table)

        # Call superclass update function to change enemy visual
        super().update(closest_player, cur_pos, player_pos, cell_table, board)

        # Move to next cell if it is further than 1 away from the player
        next_cell = board.cell_pos[path[1 if len(path) > 2 else 0][1]][path[1 if len(path) > 2 else 0][0]]

        # New x and y pos in the middle of the cell
        new_x = (next_cell.x + board.x + (next_cell.w // 2) - self.width)
        new_y = (next_cell.y + board.y + (next_cell.h // 2) - self.height)

        # Only change x and y if there isn't a large enemy already in there
        self.x, self.y = (new_x, new_y) if (new_x, new_y) not in self.l_enemy_pos else (self.x, self.y)

        # Spawn small enemy
        if randint(1, 25) == 25:
            self.spawned_enemies.append(SmallEnemy.from_large_enemy(self))


class MeleeSwing(pygame.Surface):
    """Surface which the melee swing animation is drawn to"""
    def __init__(self, owner: Player, item: str):
        # Calculate the current items melee distance if it is a melee weapon
        if DataLoader.possible_items[item].get("melee_dist") is not None:
            self.__width = MAX_MELEE_SWING_WIDTH * (DataLoader.possible_items[item]["melee_dist"] / 100)
            self.__height = MAX_MELEE_SWING_HEIGHT * (DataLoader.possible_items[item]["melee_dist"] / 100)
        else:
            self.__width = MAX_MELEE_SWING_WIDTH
            self.__height = MAX_MELEE_SWING_HEIGHT

        super().__init__((self.__width, self.__height), pygame.SRCALPHA)
        self.item = item
        self.swing = False
        self.swing_pos = (0, 0)
        self.__owner = owner
        self.__frame_num = 0
        self.left = 0
        self.right = 0
        self.x = 0
        self.y = 0

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def get_coords(self):
        """
        Calculate coords on melee_swing circle using the equation:
        (x, y) = (cx + (r * cos(angle)), cy - (r * sin(angle)))
                                            ^
                               Inverted y due to inverted axis
        :return: Coords on edge of the swing
        """
        ms_rect = pygame.Rect(
            self.x, self.y, self.width, self.height
        )
        return (
            ms_rect.centerx + ((self.width // 2) * cos(self.left)),   # x1
            ms_rect.centery - ((self.width // 2) * sin(self.left)),   # y1
            ms_rect.centerx + ((self.width // 2) * cos(self.right)),  # x2
            ms_rect.centery - ((self.width // 2) * sin(self.right))   # y2
        )

    def update(self) -> None:
        """
        Updates the MeleeSwing surface
        :return: None
        """
        self.fill((0, 0, 0, 0))

        if self.swing:
            # Counts frames
            self.__frame_num += 1

            # Gets midpoint angle and shift by 90
            midpoint = math.atan2(self.__owner.x + self.__owner.width - self.swing_pos[0], self.__owner.y + self.__owner.height - self.swing_pos[1])
            midpoint = math.radians(math.degrees(midpoint) + 90)

            # Get left most angle by doing midpoint - 30, this will allow the arc to span 60 degrees
            self.left = math.radians(math.degrees(midpoint) - 30)

            # Increment left angle by the frame num * 4, this makes the arc swipe left to right
            self.right = math.radians(math.degrees(self.left) + (self.__frame_num * 4))

            # Draw the arc to the surface and set width to frame num to allow it to enlarge over time
            pygame.draw.arc(
                self, (255, ((255 // 15) * (15 - self.__frame_num)), ((255 // 15) * (15 - self.__frame_num))),
                self.get_rect(), self.left, self.right, math.ceil(self.__frame_num / 2)
            )

        # After 15 frames stop the animation and reset frame num
        if self.__frame_num >= 15:
            self.__frame_num = 0
            self.swing = False


class Bullet(pygame.Rect):
    def __init__(self, origin_x, origin_y, target_x, target_y, weapon):
        super().__init__(origin_x, origin_y, weapon["proj_size"], weapon["proj_size"])
        self.x = origin_x
        self.y = origin_y
        self.__target_x = target_x
        self.__target_y = target_y
        self.__origin_x = origin_x
        self.__origin_y = origin_y
        self.__width = weapon["proj_size"]
        self.__height = weapon["proj_size"]
        self.__circle_radius = weapon["proj_dist"]
        self.damage = weapon["damage"]
        self.colour = tuple(weapon["colour"])
        self.moving = True
        self.from_enemy = True if weapon["item_type"] == "enemy_weapon" else False

        # Create circle function in form (x - center_x)^2 + (y - center_y)^2 = radius^2
        self.circle_eq = lambda x, y: (x - self.__origin_x) ** 2 + (y - self.__origin_y) ** 2

        # Calculate Euclidean distance from target pos to player pos
        #     _____________________________
        #    /
        #   /  (x2 - x1)^2 + (y2 - y1)^2
        # \/
        dist = math.sqrt((target_x - self.__origin_x) ** 2 + (target_y - self.__origin_y) ** 2)

        # Calculate the number of times the line can be divided by the speed
        self.__num_of_divisions = dist / (MAX_BULLET_SPEED * (weapon["proj_speed"] / 100))
        self.__cur_div = 1

    def update(self, dt: float) -> None:
        """
        Updates the Bullet class
        To move the bullet this equation is used:
            (x, y) = (x1 + k(x2 - x1), y1 + k(y2 - y1))

            where (x1, y1) is the start point,
                  (x2, y2) is the endpoint,
                  k is the fraction of the line you want to divide
        :param dt: Delta time
        :return: None
        """
        # Checks if (x - center_x)^2 + (y - center_y)^2 < radius^2
        # and if so then the bullet is still within the circle and can be drawn and moved
        if self.circle_eq(self.x, self.y) < self.__circle_radius ** 2:

            new_x = self.__origin_x + ((self.__cur_div / self.__num_of_divisions) * (self.__target_x - self.__origin_x))
            new_y = self.__origin_y + ((self.__cur_div / self.__num_of_divisions) * (self.__target_y - self.__origin_y))

            # Scale using delta time
            scaled_x = (new_x - self.x) * dt
            scaled_y = (new_y - self.y) * dt

            self.x += scaled_x
            self.y += scaled_y

            self.__cur_div += 1
        else:
            self.moving = False


@dataclass
class Bezier:
    control_points: list
    num_of_points: int

    def get_points(self):
        control_x, control_y = zip(*self.control_points)
        return [
            (
                int(self.__B(control_x, 0, len(self.control_points) - 1, t / self.num_of_points)),
                int(self.__B(control_y, 0, len(self.control_points) - 1, t / self.num_of_points))
            )
            for t in range(self.num_of_points)
        ]

    def __B(self, arr: list, i: int, j: int, t: float) -> float:
        """
        Using De Casteljau's algorithm:
        Gets the one dimensional value of the coords at the provided i value
        Recurrence relation:
            B(i, j) = B(i, j - 1) * (1 - t) + B(i + 1, j - 1) * t
        """
        return arr[i] if j == 0 else self.__B(arr, i, j - 1, t) * (1 - t) + self.__B(arr, i + 1, j - 1, t) * t


class TeleportAnimation(pygame.Surface):
    def __init__(self, x, y, angle):
        self.__width = CELL_WIDTH + WALL_VERTICAL_WIDTH
        self.__height = ENTITY_INFO["large"][1]
        super().__init__((self.__width, self.__height), pygame.SRCALPHA)
        self.x = x
        self.y = y
        self.angle = angle
        self.divs = 15
        self.__segments = [pygame.Rect((self.__width // self.divs) * i, 0, self.__width // self.divs, self.__height) for i in range(self.divs)]
        self.__cur_frame = 0
        self.__colour_grad = [i for i in colour_lerp((255, 255, 255), (255, 60, 0), self.divs)]

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def update(self):
        # takes 30 frames
        self.fill((0, 0, 0, 0))
        if self.__cur_frame < 15:
            for i in range(self.__cur_frame):
                pygame.draw.rect(self, self.__colour_grad[i], self.__segments[i])
            self.__cur_frame += 1
        elif 15 <= self.__cur_frame <= 30:
            for i in range(self.__cur_frame - 15, 15):
                pygame.draw.rect(self, self.__colour_grad[i], self.__segments[i])
            self.__cur_frame += 1


if __name__ == '__main__':
    pass
