import pygame
from ui import Hotbar, Inventory, Inspector, Equipment, Attributes, Tab, HealthBar, ManaBar, XPBar, SkillTree, ItemDropDisplay
from board import Board
from entities import Player, SmallEnemy, MediumEnemy, LargeEnemy, MeleeSwing, Bullet
from data_loader import DataLoader
from maze_creator import MazeCreator
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, MAIN_ASSET_PATH
from random import randint
from items import ItemDrop
from typing import Iterable
from math import sin, cos
pygame.init()

width, height = WINDOW_WIDTH, WINDOW_HEIGHT
display = pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
clock = pygame.time.Clock()
pygame.mouse.set_cursor(*pygame.cursors.broken_x)

# Define player name here, this is then set as class attribute rather than instance
# DataLoader then created to call __init__ to load the player data
PLAYER_NAME = "alex"
DataLoader.player_name = PLAYER_NAME
_ = DataLoader()

# Create new maze
maze = MazeCreator(10, 10)
maze.create((0, 0))

# Create all game surfaces
hotbar = Hotbar()
inv = Inventory()
inspector = Inspector()
tab = Tab()
equipment = Equipment()
attributes = Attributes()
xp_bar = XPBar()
item_drop_display = ItemDropDisplay()
board = Board(2050, 2050)
st = SkillTree(width, height)

# Create entities
player = Player()
s_enemy = SmallEnemy(950, 190)
m_enemy = MediumEnemy(190, 190)
l_enemy = LargeEnemy(190, 190)
melee_swing = MeleeSwing(player, hotbar[hotbar.selected_pos][1])

healthbar = HealthBar(player.health)
manabar = ManaBar(player.mana)

# Misc Variables
font = pygame.font.SysFont("Courier", 15, True)
running = True
show_inv = False
show_equipment = True
show_st = False
show_menu = False
name = None
data = None
mx, my = 0, 0
go_right, go_left, go_up, go_down, = False, False, False, False
num_pos = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: 4, pygame.K_5: 5}
mid_screen = pygame.Rect(0, (height // 2) - 200, width, height // 2)
enemies = [MediumEnemy((380 * randint(1, 5)) - 190, (380 * randint(1, 5)) - 190) for i in range(10)]
frames = 60
item_drops = []
bullets = []


def inv_collide() -> tuple:
    """
    Checks if the mouse collides with any of the items
    :return: The position in the inventory items list, Rect object of which the mouse collides with
    """
    # Loops through inv using __getitem__
    for pos, space in enumerate(inv):
        rect = pygame.Rect((inv.width // 2) + space[1].x, (inv.height // 2) + space[1].y, space[1].w, space[1].h)
        if rect.collidepoint(mx, my):
            return pos, space


def eq_collide() -> tuple:
    """
    Checks if the mouse collides with any of the equipment
    :return: The position in the equipment items list, Rect object of which the mouse collides with
    """
    for pos, slot in enumerate(equipment):
        rect = pygame.Rect(slot[1].x, (height // 2 - (equipment.height // 2)) + slot[1].y, slot[1].w, slot[1].h)
        if rect.collidepoint(mx, my):
            return pos, slot


def st_collide() -> tuple:
    """
    Checks if mouse collides with any of the skill tree rects
    :return: The space that was collided with
    """
    for space in st:
        rect = pygame.Rect(space[1].x, space[1].y + (height // 2 - (st.height // 2)), space[1].w, space[1].h)
        if rect.collidepoint(mx, my):
            return space


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


def bullet_collide(b):
    adjusted_b = pygame.Rect(b.x + board.x, b.y + board.y, b.w, b.h)
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


def get_rect_lines(r) -> list:
    return [
        (r.x, r.y),
        (r.x + r.width, r.y),
        (r.x + r.width, r.y + r.height),
        (r.x, r.y + r.height)
    ]


def kill_enemy(index):
    drop_data = enemies[index].kill()
    del enemies[index]

    if drop_data is not None:
        drop_data = drop_data[0] - board.x, drop_data[1] - board.y, drop_data[2]
        item_drops.append(ItemDrop(*drop_data))


while running and player.health > 0:
    # Calculate real time since last frame to scale movement
    time_since_last_tick = clock.tick(frames)
    normal_ms_per_frame = 1000 / frames
    delta_time_scalar = time_since_last_tick / normal_ms_per_frame
    mv_amount = player.mv_amount * delta_time_scalar

    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Quits game
            if event.key == pygame.K_ESCAPE:
                running = False
            # Toggles inventory
            elif event.key == pygame.K_e:
                show_inv = not show_inv
                show_st = False
            # Switches tabs
            elif event.key == pygame.K_i:
                show_equipment = not show_equipment
                tab.selected_equipment = not tab.selected_equipment
            elif event.key == pygame.K_k:
                show_st = not show_st
                show_inv = False
            # Adds xp to player -------------------------------------------------- Dev tool
            elif event.key == pygame.K_x:
                DataLoader.change_file("add_xp", 1)
            # Removes health and mana from player -------------------------------- Dev tool
            elif event.key == pygame.K_h:
                player.health -= 10
                player.mana -= 10 if player.mana - 10 >= 0 else 0
            elif event.key == pygame.K_y:
                frames = 2
            elif event.key == pygame.K_v:
                kill_enemy(randint(0, len(enemies) - 1))

            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                if show_inv:
                    inv_collide_data = inv_collide()
                    if inv_collide_data is not None:
                        pos, space = inv_collide_data
                        DataLoader.change_file("remove_from_hotbar", num_pos[event.key] - 1)
                        DataLoader.change_file("add_to_hotbar", space[0][1], num_pos[event.key] - 1)
                        DataLoader.change_file("remove_from_inv", pos)
                        DataLoader.change_file("add_to_inv", hotbar[num_pos[event.key] - 1][1], pos)

            # Movement keys
            elif event.key == pygame.K_d:
                go_right = True
            elif event.key == pygame.K_a:
                go_left = True
            elif event.key == pygame.K_w:
                go_up = True
            elif event.key == pygame.K_s:
                go_down = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                go_right = False
            elif event.key == pygame.K_a:
                go_left = False
            elif event.key == pygame.K_w:
                go_up = False
            elif event.key == pygame.K_s:
                go_down = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if show_inv:
                    mx, my = pygame.mouse.get_pos()
                    # Changing attribute tab
                    for pos, sect in enumerate(tab):
                        rect = pygame.Rect(sect.x, tab.height * 2 + sect.y, sect.w, sect.h)
                        if rect.collidepoint(mx, my):
                            tab.selected_equipment = True if pos == 0 else False
                            show_equipment = True if pos == 0 else False

                    # Changing attribute numbers
                    for pos, signs in enumerate(attributes):
                        plus, minus = signs
                        p = pygame.Rect(plus.x, (height // 2 - (attributes.height // 2)) + plus.y, plus.w, plus.h)
                        m = pygame.Rect(minus.x, (height // 2 - (attributes.height // 2)) + minus.y, minus.w, minus.h)
                        if p.collidepoint(mx, my):
                            DataLoader.change_file("increment_attr", list(DataLoader.player_data["attributes"])[pos], 1)
                        if m.collidepoint(mx, my):
                            DataLoader.change_file("increment_attr", list(DataLoader.player_data["attributes"])[pos], -1)

            # Switch armor for current selected using right mouse
            elif event.button == 3:
                if show_inv:
                    inv_collide_data = inv_collide()
                    if inv_collide_data is not None:
                        pos, space = inv_collide_data
                        for i_pos, tup in enumerate(inv):
                            if tup[1] == space[1] and DataLoader.possible_items[tup[0][1]]["item_type"] == "armor":
                                armor_type = DataLoader.possible_items[tup[0][1]]["armor_type"]
                                DataLoader.change_file("remove_from_inv", i_pos)
                                DataLoader.change_file("add_to_inv", DataLoader.player_data["armor"][armor_type], i_pos)
                                DataLoader.change_file("remove_from_armor", armor_type)
                                DataLoader.change_file("add_to_armor", armor_type, tup[0][1])

            elif event.button == 4:
                hotbar.change_selected(-1)
            elif event.button == 5:
                hotbar.change_selected(1)

    # Player movement
    if not show_inv:
        collided_with_door = board.door_collide(player)
        collided_with_wall = board.wall_collide(player)
        if (collided_with_door == "not on door" and not collided_with_wall) or collided_with_door == "door open":
            if go_right:
                player_rect = pygame.Rect(player.x + mv_amount, player.y, player.width, player.height)
                if (board.door_collide(player_rect) == "not on door" and not board.wall_collide(player_rect)) or board.door_collide(player_rect) == "door open":
                    if pygame.Rect(board.x - mv_amount, board.y, board.width, board.height).contains(display.get_rect()) and mid_screen.collidepoint(player.x, player.y):
                        board.x -= mv_amount
                        for enemy in enemies:
                            enemy.x -= mv_amount
                    else:
                        player.x += mv_amount
            if go_left:
                player_rect = pygame.Rect(player.x - mv_amount, player.y, player.width, player.height)
                if (board.door_collide(player_rect) == "not on door" and not board.wall_collide(player_rect)) or board.door_collide(player_rect) == "door open":
                    if pygame.Rect(board.x + mv_amount, board.y, board.width, board.height).contains(display.get_rect()) and mid_screen.collidepoint(player.x, player.y):
                        board.x += mv_amount
                        for enemy in enemies:
                            enemy.x += mv_amount
                    else:
                        player.x -= mv_amount
            if go_up:
                player_rect = pygame.Rect(player.x, player.y - mv_amount, player.width, player.height)
                if (board.door_collide(player_rect) == "not on door" and not board.wall_collide(player_rect)) or board.door_collide(player_rect) == "door open":
                    if pygame.Rect(board.x, board.y + mv_amount, board.width, board.height).contains(display.get_rect()) and mid_screen.collidepoint(player.x, player.y):
                        board.y += mv_amount
                        for enemy in enemies:
                            enemy.y += mv_amount
                    else:
                        player.y -= mv_amount
            if go_down:
                player_rect = pygame.Rect(player.x, player.y + mv_amount, player.width, player.height)
                if (board.door_collide(player_rect) == "not on door" and not board.wall_collide(player_rect)) or board.door_collide(player_rect) == "door open":
                    if pygame.Rect(board.x, board.y - mv_amount, board.width, board.height).contains(display.get_rect()) and mid_screen.collidepoint(player.x, player.y):
                        board.y -= mv_amount
                        for enemy in enemies:
                            enemy.y -= mv_amount
                    else:
                        player.y += mv_amount

    # Gets mouse position
    mx, my = pygame.mouse.get_pos()

    # Mouse collision to provide the inspector with data
    if show_inv:
        inv_collide_data = inv_collide()
        if inv_collide_data is not None:
            pos, space = inv_collide_data
            name = space[0][1]
            data = {
                "img": space[0][0],
                "attr": DataLoader.possible_items[space[0][1]],
                "inv_pos": pos,
                "eq_pos": None,
                "st_pos": None
            }

        if show_equipment:
            eq_collide_data = eq_collide()
            if eq_collide_data is not None:
                pos, slot = eq_collide_data
                name = slot[0][1]
                data = {
                    "img": slot[0][0],
                    "attr": DataLoader.possible_items[slot[0][1]],
                    "eq_pos": pos,
                    "inv_pos": None,
                    "st_pos": None
                }
    if show_st:
        st_collide_data = st_collide()
        if st_collide_data is not None:
            skill, rect, img = st_collide_data
            name = skill["elem"].tag
            data = {
                "img": img,
                "attr": {**skill["elem"].attrib, "level": DataLoader.player_data["skills"].get(name)},
                "eq_pos": None,
                "inv_pos": None,
                "st_pos": rect
            }

    player_cell_y, player_cell_x = board.cell_collide(player)
    player_puz_x, player_puz_y = maze.cell_table[player_cell_x, player_cell_y]

    # Item drop pickup
    for it_dr_pos, it_dr in enumerate(item_drops):
        player_rect = pygame.Rect(player.x - board.x, player.y - board.y, player.width, player.height)
        item_rect = pygame.Rect(it_dr.x, it_dr.y, it_dr.width, it_dr.height)
        if player_rect.colliderect(item_rect):
            next_slot = DataLoader.get_next_open_inv_slot()
            if next_slot is not None:
                DataLoader.change_file("remove_from_inv", next_slot)
                DataLoader.change_file("add_to_inv", it_dr.item.name, next_slot)
                item_drop_display.add_item((it_dr.item.name, pygame.image.load(MAIN_ASSET_PATH + it_dr.item.name + ".png")))
                del item_drops[it_dr_pos]

    for button, pressed in enumerate(pygame.mouse.get_pressed()):
        if button == 0 and pressed == 1:
            cur_item = DataLoader.possible_items[hotbar[hotbar.selected_pos][1]]
            if not show_inv and not show_st and not show_menu:
                if cur_item.get("melee_speed") is not None:
                    speed = cur_item["melee_speed"]
                    damage = cur_item["damage"]
                    if player.melee_cooldown >= (60 * (1 - (speed / 100))):
                        player.melee_cooldown = 0
                        melee_swing.swing = True
                        melee_swing.swing_pos = pygame.mouse.get_pos()

                elif cur_item.get("proj_dist") is not None:
                    if cur_item.get("mana_used") is not None:
                        if player.mana - cur_item["mana_used"] >= 0:
                            # player.mana -= cur_item["mana_used"]
                            bullets.append(
                                Bullet(
                                    abs(board.x) + player.x + player.width,
                                    abs(board.y) + player.y + player.height,
                                    abs(board.x) + mx,
                                    abs(board.y) + my,
                                    cur_item
                                )
                            )
                    else:
                        # Arrow
                        pass

    if melee_swing.swing and melee_swing.left > 0 and melee_swing.right > 0:
        damage = DataLoader.possible_items[hotbar[hotbar.selected_pos][1]]["damage"]
        ms_rect = pygame.Rect(melee_swing.x, melee_swing.y, melee_swing.width, melee_swing.height)
        # Calculate coords on melee_swing circle using the equation:
        # (x, y) = (cx + (r * cos(angle)), cy - (r * sin(angle)))
        #                                     ^
        #                        Inverted y due to inverted axis
        melee_swing_coords = (
            ms_rect.centerx + ((melee_swing.width // 2) * cos(melee_swing.left)),
            ms_rect.centery - ((melee_swing.width // 2) * sin(melee_swing.left)),
            ms_rect.centerx + ((melee_swing.width // 2) * cos(melee_swing.right)),
            ms_rect.centery - ((melee_swing.width // 2) * sin(melee_swing.right))
        )
        for e in enemies:
            enemy_lines = get_rect_lines(pygame.Rect(e.x + (e.width // 2), e.y + (e.height // 2), e.width, e.height))
            hits = [line_collide(melee_swing_coords, (*enemy_lines[a], *enemy_lines[b])) for a, b in zip(range(4), [1, 2, 3, 0])]
            if any(hits):
                e.health -= damage
                print(e.health)

    # Kill enemy if health < 1
    for pos, e in enumerate(enemies):
        if e.health < 1:
            kill_enemy(pos)

    player.melee_cooldown += 1

    # Fill the display with black to draw on top of
    display.fill((0, 0, 0))

    # Update board surface
    board.update()

    # Draw item drops to screen
    for it_dr in item_drops:
        it_dr.update()
        board.blit(it_dr, (it_dr.x, it_dr.y))

    # Draw bullets to screen
    for bullet in bullets:
        bullet_collided = bullet_collide(bullet)
        if bullet_collided:
            bullet.moving = False
        if bullet.moving:
            bullet.update(delta_time_scalar)
            pygame.draw.rect(board, bullet.colour, bullet)
        else:
            bullets.remove(bullet)

    # Draw board to screen
    display.blit(board, (board.x, board.y))

    # Draw enemies to screen
    for enemy in enemies:
        r, c = board.cell_collide(enemy)
        puz_x, puz_y = maze.cell_table[c, r]
        enemy.update(player, (puz_x, puz_y), (player_puz_x, player_puz_y), maze.cell_table, board)
        display.blit(enemy, (enemy.x, enemy.y))

    # Draw player to screen
    mx, my = pygame.mouse.get_pos()
    player.update(mx, my)
    display.blit(player, (player.x, player.y))

    # Draw melee swing to screen
    if hotbar[hotbar.selected_pos][1] != melee_swing.item:
        melee_swing = MeleeSwing(player, hotbar[hotbar.selected_pos][1])
    melee_swing.update()
    p_rect = pygame.Rect(player.x + (player.width // 2), player.y + (player.height // 2), player.width, player.height)
    melee_swing.x = p_rect.centerx - (melee_swing.width // 2)
    melee_swing.y = p_rect.centery - (melee_swing.height // 2)
    display.blit(melee_swing, (melee_swing.x, melee_swing.y))

    # Update hotbar surface and draw to screen
    hotbar.update()
    display.blit(hotbar, (width // 3, height - hotbar.height))

    # Update health bar surface and draw to screen
    healthbar.update(font, player.health)
    display.blit(healthbar, (width // 20, height - (hotbar.height - hotbar.height // 4)))

    # Update mana bar surface and draw to screen
    manabar.update(font, player.mana)
    display.blit(manabar, ((width // 20) * 15, height - (hotbar.height - hotbar.height // 4)))

    # Update item drop display and draw to screen
    item_drop_display.update(font)
    display.blit(item_drop_display, (width - item_drop_display.width, height // 2 - (item_drop_display.height // 1.5)))

    # Update inventory surface and draw to screen
    if show_inv:
        inv.update(data)
        display.blit(inv, (width // 2 - (inv.width // 2), height // 2 - (inv.height // 2)))

    # Update inspector if inventory or skill tree is open
    if show_inv or show_st:
        inspector.update(name, font, data)
        display.blit(inspector, (width - inspector.width, height // 2 - (inspector.height // 2)))

    # Update equipment if inventory is open and equipment is selected
    if show_inv and show_equipment:
        equipment.update(font, data)
        display.blit(equipment, (0, height // 2 - (equipment.height // 2)))

    # Update attributes if inventory is open and attributes is selected
    if show_inv and not show_equipment:
        attributes.update(font)
        display.blit(attributes, (0, height // 2 - (attributes.height // 2)))

    # Update tab if inventory is open
    if show_inv:
        tab.update(font)
        display.blit(tab, (0, height // 2 - (attributes.height // 2)))

    # Update XP bar if inventory is open
    if show_inv:
        xp_bar.update(font)
        display.blit(xp_bar, (width // 2 - (inv.width // 2), height // 2 - (inv.height // 2) - xp_bar.height))

    # Update skill tree surface
    if show_st:
        st.update(font, data)
        display.blit(st, (0, height // 2 - (st.height // 2)))

    # Update whole screen
    pygame.display.update()

pygame.quit()
