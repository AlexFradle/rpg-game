import pygame
from items import ItemDrop
from typing import Iterable, Union
from constants import WINDOW_HEIGHT
from ui import Inventory, Equipment, SkillTree
from board import Board
from data_loader import DataLoader


def line_collide(line_1_coords: Iterable, line_2_coords: Iterable) -> tuple:
    """
    Line-Line Collision using the equation:


            (x1 - x3)(y3 - y4) - (y1 - y3)(x3 - x4)
        t = ─────────────────────────────────────────────
            (x1 - x2)(y3 - y4) - (y1 - y2)(x3 - x4)


              (x1 - x2)(y1 - y3) - (y1 - y2)(x1 - x3)
        u = - ─────────────────────────────────────────────
              (x1 - x2)(y3 - y4) - (y1 - y2)(x3 - x4)


        (Px, Py) = (x1 + t(x2 - x1), y1 + t(y2 - y1))
                             or
        (Px, Py) = (x3 + u(x4 - x3), y3 + u(y4 - y3))


    t and u are used to turn the infinite lines into line segments

    t and u can also be used to determine if there is a collision before calculating coords because:
        0.0 ≤ t ≤ 1.0
        0.0 ≤ u ≤ 1.0
    if t or u is outside of this range then there is no collision

    :param line_1_coords: (x1, y1, x2, y2)
    :param line_2_coords: (x3, y3, x4, y4)
    :return: Collision coords
    """
    # Unpacking argument iterable
    x1, y1, x2, y2 = line_1_coords
    x3, y3, x4, y4 = line_2_coords

    # Calculating t and u
    t = ((((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))))
    u = -((((x1 - x2) * (y1 - y3)) - ((y1 - y2) * (x1 - x3))) / (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))))

    # Calculating intersection coords
    px = x1 + (t * (x2 - x1))
    py = y1 + (t * (y2 - y1))

    return (px, py) if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0 else False


def colour_lerp(a: Union[tuple, list], b: Union[tuple, list], num_of_cols: int) -> tuple:
    """
    Colour linear interpolation between c1 and c2
    Uses the equation:
        Cr = Ar + t(Br - Ar)
        Cg = Ag + t(Bg - Ag)
        Cb = Ab + t(Bb - Ab)

        0.0 ≤ t ≤ 1.0

        Where:
            A is the start colour,
            B is the end colour,
            C is the interpolated colour

    :param a:
    :param b:
    :param num_of_cols:
    :return:
    """
    for t in range(num_of_cols + 1):
        t /= num_of_cols
        c = (a[0] + (t * (b[0] - a[0])), a[1] + (t * (b[1] - a[1])), a[2] + (t * (b[2] - a[2])))
        yield c


def inv_collide(inv: Inventory, mx: int, my: int) -> tuple:
    """
    Checks if the mouse collides with any of the items
    :param inv: Inventory object to check collision on
    :param mx: Mouse x pos
    :param my: Mouse y pos
    :return: The position in the inventory items list, Rect object of which the mouse collides with
    """
    # Loops through inv using __getitem__
    for pos, space in enumerate(inv):
        rect = pygame.Rect((inv.width // 2) + space[1].x, (inv.height // 2) + space[1].y, space[1].w, space[1].h)
        if rect.collidepoint(mx, my):
            return pos, space


def eq_collide(eq: Equipment, mx: int, my: int) -> tuple:
    """
    Checks if the mouse collides with any of the equipment
    :param eq: Equipment object to check collision on
    :param mx: Mouse x pos
    :param my: Mouse y pos
    :return: The position in the equipment items list, Rect object of which the mouse collides with
    """
    for pos, slot in enumerate(eq):
        rect = pygame.Rect(slot[1].x, (WINDOW_HEIGHT // 2 - (eq.height // 2)) + slot[1].y, slot[1].w, slot[1].h)
        if rect.collidepoint(mx, my):
            return pos, slot


def st_collide(st: SkillTree, mx: int, my: int) -> tuple:
    """
    Checks if mouse collides with any of the skill tree rects
    :param st: SkillTree object to check collision on
    :param mx: Mouse x pos
    :param my: Mouse y pos
    :return: The space that was collided with
    """
    for space in st:
        rect = pygame.Rect(space[1].x, space[1].y + (WINDOW_HEIGHT // 2 - (st.height // 2)), space[1].w, space[1].h)
        if rect.collidepoint(mx, my):
            return space


def bullet_collide(b, board: Board, player, enemies: list) -> bool:
    """
    Checks if the bullet has collided with any surfaces
    :param b: Bullet object to check collision with
    :param board: Board object that the bullet is being drawn to
    :param player: Player object to check collision on
    :param enemies: All enemies currently alive
    :return: True if collided, False if not
    """
    adjusted_b = pygame.Rect(b.x + board.x, b.y + board.y, b.w, b.h)
    if b.from_enemy:
        pl_rect = pygame.Rect(player.x + (player.width // 2), player.y + (player.height // 2), player.width, player.height)
        if adjusted_b.colliderect(pl_rect):
            player.health -= b.damage
            return True
    else:
        for e in enemies:
            e_rect = pygame.Rect(e.x + (e.width // 2), e.y + (e.height // 2), e.width, e.height)
            if adjusted_b.colliderect(e_rect):
                e.health -= b.damage
                return True

    for vws, hws, vds, hds in zip(board.vert_wall_pos, board.hori_wall_pos, board.vert_door_pos, board.hori_door_pos):
        for vw, hw, vd, hd in zip(vws, hws, vds, hds):
            if b.colliderect(vw) or b.colliderect(hw):
                if (b.colliderect(vd) and vd.open_) or (b.colliderect(hd) and hd.open_):
                    return False
                else:
                    return True
    return False


def get_rect_corners(r: pygame.Rect) -> list:
    """
    Gets each corner (x, y) of rect
    :param r: Rect to get corners of
    :return: List of 4 (x, y) coords corresponding to each corner in a clockwise direction from top left
    """
    return [
        (r.x, r.y),
        (r.x + r.width, r.y),
        (r.x + r.width, r.y + r.height),
        (r.x, r.y + r.height)
    ]


def kill_enemy(enemies: list, index: int, board: Board, item_drops: list) -> list:
    """
    Kills the enemy provided and gets loot drop
    :param enemies: List of all enemies currently alive
    :param index: Index in enemies list of the enemy to kill
    :param board: Board object
    :param item_drops: List of all item drops currently on the board
    :return: Updated item_drops list
    """
    drop_data = enemies[index].kill()
    del enemies[index]

    if drop_data is not None:
        DataLoader.change_file("add_xp", drop_data[3])
        drop_data = drop_data[0] - board.x, drop_data[1] - board.y, drop_data[2]
        item_drops.append(ItemDrop(*drop_data))
        return item_drops


def get_teleport_position(tpa, board):
    return {
        0: (tpa.x + tpa.height + board.x, tpa.y + board.y),
        90: (tpa.x + board.x, tpa.y - tpa.width + board.y),
        180: (tpa.x - tpa.width + board.x, tpa.y + board.y),
        270: (tpa.x + board.x, tpa.y + tpa.height + board.y)
    }[tpa.angle]
