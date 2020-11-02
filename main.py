import pygame
from ui import Hotbar, Inventory, Inspector, Equipment, Attributes, Tab, HealthBar, ManaBar, XPBar, SkillTree, \
    ItemDropDisplay, Menu, SelectMenu
from board import Board
from entities import Player, SmallEnemy, MediumEnemy, LargeEnemy, MeleeSwing, Bullet, Bezier, PseudoBullet
from data_loader import DataLoader
from maze_creator import MazeCreator
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, MAIN_ASSET_PATH, BEZIER_POINT_COLOUR, GNS_IP, \
    GNS_PORT, SELECT_MENU_WIDTH, MENU_WIDTH, MENU_HEIGHT, SELECT_MENU_HEIGHT, GAME_TITLE, TEXT_COLOUR
from random import randint
from utils import line_collide
from items import ItemDrop
from network import GameServer, GameClient
from os import environ
import socket
import json
import subprocess
import threading
pygame.init()

environ["SDL_VIDEO_CENTERED"] = "1"

width, height = WINDOW_WIDTH, WINDOW_HEIGHT
window = pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
clock = pygame.time.Clock()
pygame.mouse.set_cursor(*pygame.cursors.broken_x)


class Display(pygame.Surface):
    def __init__(self, w, h):
        super().__init__((w, h), pygame.SRCALPHA)
        self.width = w
        self.height = h

        # Create new maze
        self.maze = MazeCreator(10, 10)
        self.maze.create((0, 0))

        self.start_menu = Menu((WINDOW_WIDTH - (SELECT_MENU_WIDTH + MENU_WIDTH)) // 2, WINDOW_HEIGHT - MENU_HEIGHT, [
            ("Singleplayer", lambda: exec("start_single_game = True", globals())),
            ("Join Game", lambda: exec("join_multiplayer_pressed = True", globals())),
            ("Create Game", lambda: exec("start_multiplayer_game = True", globals())),
            ("Quit", lambda: exec("game_on = False", globals()))
        ])
        self.pause_menu = Menu(WINDOW_WIDTH // 2 - (MENU_WIDTH // 2), WINDOW_HEIGHT // 2 - (MENU_HEIGHT // 2), [
            ("Resume", lambda: exec("game.show_menu = False", globals())),
            ("Help", lambda: exec("")),
            ("Quit", lambda: exec(
                "game.running = False;"
                "start_single_game = False;"
                "start_multiplayer_game = False;"
                "join_multiplayer_game = False;"
                "join_multiplayer_pressed = False;"
                "start_screen = True",
                globals()
            ))
        ])
        self.character_menu = SelectMenu(((WINDOW_WIDTH - (SELECT_MENU_WIDTH + MENU_WIDTH)) // 2) + MENU_WIDTH, WINDOW_HEIGHT - MENU_HEIGHT, [
            (
                (name, DataLoader.all_player_data[name]["class"], "lvl " + str(DataLoader.all_player_data[name]["level"])),
                lambda a: exec(f"character_selected = '{a}';", globals())
            ) for name in DataLoader.all_player_data
        ])


class Game:
    def __init__(self, display, is_host, is_singleplayer, name, server_ip=None, server_port=None, host_address=None):
        # Define player name here, this is then set as class attribute rather than instance
        # DataLoader then created to call __init__ to load the player data
        DataLoader.player_name = name
        _ = DataLoader()
        self.display = display
        self.is_host = is_host
        self.is_singleplayer = is_singleplayer
        self.player_name = name

        # Create all game surfaces
        self.hotbar = Hotbar()
        self.inv = Inventory()
        self.inspector = Inspector()
        self.tab = Tab()
        self.equipment = Equipment()
        self.attributes = Attributes()
        self.xp_bar = XPBar()
        self.item_drop_display = ItemDropDisplay()
        self.st = SkillTree(display.width, display.height)

        # Create entities
        self.player = Player(self.player_name, 1)
        self.enemies = []

        # Misc Variables
        self.font = pygame.font.SysFont("Courier", 15, True)
        self.running = True
        self.show_inv = False
        self.show_equipment = True
        self.show_st = False
        self.show_menu = False
        self.name = None
        self.data = None
        self.grid = None
        self.num_pos = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: 4, pygame.K_5: 5}
        self.enemies = {i: LargeEnemy((380 * randint(1, 5)) - 190, (380 * randint(1, 5)) - 190, self.is_host) for i in range(2)}
        self.frames = 30
        self.item_drops = []
        self.bullets = {self.player_name: {}}
        self.other_players = {}
        self.next_enemy_index = 2
        self.next_bullet_index = 0

        # Networking
        # Host of multiplayer game
        if self.is_host and not self.is_singleplayer:
            self.game_server = GameServer(server_ip, server_port, self)
            threading.Thread(target=self.game_server.start, daemon=True).start()

        # Client of multiplayer game
        elif not self.is_host and not self.is_singleplayer:
            self.client = GameClient(host_address.split(":")[0], int(host_address.split(":")[1]), self)
            self.client.connect()

        # Make melee swing using correct player
        self.melee_swing = MeleeSwing(self.player, self.hotbar[self.hotbar.selected_pos][1])

        # Use new maze if host, else inherit the host maze
        self.board = Board() if self.is_host else Board(grid=self.grid)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def bullet_collide(b, board: Board, player, enemies: dict) -> bool:
        """
        Checks if the bullet has collided with any surfaces
        :param b: Bullet object to check collision with
        :param board: Board object that the bullet is being drawn to
        :param player: Player object to check collision on
        :param enemies: All enemies currently alive
        :return: True if collided, False if not
        """
        pl_rect = pygame.Rect(
            player.x + (player.width // 2), player.y + (player.height // 2), player.width, player.height
        )

        # Instead of adjusting player the bullet is adjusted, no reason
        adjusted_b = pygame.Rect(b.x + board.x, b.y + board.y, b.w, b.h)

        if isinstance(b, PseudoBullet):
            if b.from_enemy:
                if adjusted_b.colliderect(pl_rect):
                    player.health -= b.damage
                    return True
        else:
            if b.from_enemy:
                if adjusted_b.colliderect(pl_rect):
                    player.health -= b.damage
                    return True
            else:
                for e in enemies.values():
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

    @staticmethod
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

    @staticmethod
    def kill_enemy(enemies: dict, index: int, board: Board, item_drops: list) -> list:
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

    def start(self):
        healthbar = HealthBar(self.player.health)
        manabar = ManaBar(self.player.mana)
        go_right, go_left, go_up, go_down, = False, False, False, False
        mid_screen = pygame.Rect(0, (self.display.height // 2) - 200, self.display.width, self.display.height // 2)
        while self.running and self.player.health > 0:
            # Calculate real time since last frame to scale movement
            time_since_last_tick = clock.tick(self.frames)
            normal_ms_per_frame = 1000 / self.frames
            delta_time_scalar = time_since_last_tick / normal_ms_per_frame
            mv_amount = self.player.mv_amount * delta_time_scalar

            # Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    # Toggles pause
                    if event.key == pygame.K_ESCAPE:
                        self.show_menu = not self.show_menu
                        self.show_inv = False
                        self.show_st = False

                    # Toggles inventory
                    elif event.key == pygame.K_e and not self.show_menu:
                        self.show_inv = not self.show_inv
                        self.show_st = False

                    # Switches tabs
                    elif event.key == pygame.K_i and not self.show_menu:
                        self.show_equipment = not self.show_equipment
                        self.display.tab.selected_equipment = not self.display.tab.selected_equipment

                    # Toggles skill tree
                    elif event.key == pygame.K_k and not self.show_menu:
                        self.show_st = not self.show_st
                        self.show_inv = False

                    # Moves item from inv to hotbar
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5] and not self.show_menu:
                        if self.show_inv:
                            inv_collide_data = self.inv_collide(self.inv, *pygame.mouse.get_pos())
                            if inv_collide_data is not None:
                                pos, space = inv_collide_data
                                DataLoader.change_file("remove_from_hotbar", self.num_pos[event.key] - 1)
                                DataLoader.change_file("add_to_hotbar", space[0][1], self.num_pos[event.key] - 1)
                                DataLoader.change_file("remove_from_inv", pos)
                                DataLoader.change_file("add_to_inv", self.hotbar[self.num_pos[event.key] - 1][1], pos)

                    # Movement keys
                    elif event.key == pygame.K_d and not self.show_menu:
                        go_right = True
                    elif event.key == pygame.K_a and not self.show_menu:
                        go_left = True
                    elif event.key == pygame.K_w and not self.show_menu:
                        go_up = True
                    elif event.key == pygame.K_s and not self.show_menu:
                        go_down = True

                if event.type == pygame.KEYUP and not self.show_menu:
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
                        if self.show_inv:
                            mx, my = pygame.mouse.get_pos()
                            # Changing attribute tab
                            for pos, sect in enumerate(self.display.tab):
                                rect = pygame.Rect(sect.x, self.display.tab.height * 2 + sect.y, sect.w, sect.h)
                                if rect.collidepoint(mx, my):
                                    self.display.tab.selected_equipment = True if pos == 0 else False
                                    self.show_equipment = True if pos == 0 else False

                            # Changing attribute numbers
                            for pos, signs in enumerate(self.attributes):
                                plus, minus = signs
                                p = pygame.Rect(
                                    plus.x,
                                    (self.display.height // 2 - (self.attributes.height // 2)) + plus.y,
                                    plus.w,
                                    plus.h
                                )
                                m = pygame.Rect(
                                    minus.x,
                                    (self.display.height // 2 - (self.attributes.height // 2)) + minus.y,
                                    minus.w,
                                    minus.h
                                )
                                if p.collidepoint(mx, my):
                                    DataLoader.change_file(
                                        "increment_attr", list(DataLoader.player_data["attributes"])[pos], 1
                                    )
                                if m.collidepoint(mx, my):
                                    DataLoader.change_file(
                                        "increment_attr", list(DataLoader.player_data["attributes"])[pos], -1
                                    )

                        if self.show_menu:
                            self.display.pause_menu.check_pressed(*pygame.mouse.get_pos())

                    # Switch armor for current selected using right mouse
                    elif event.button == 3:
                        if self.show_inv:
                            inv_collide_data = self.inv_collide(self.inv, *pygame.mouse.get_pos())
                            if inv_collide_data is not None:
                                pos, space = inv_collide_data
                                for i_pos, tup in enumerate(self.inv):
                                    if tup[1] == space[1] and DataLoader.possible_items[tup[0][1]]["item_type"] == "armor":
                                        armor_type = DataLoader.possible_items[tup[0][1]]["armor_type"]
                                        DataLoader.change_file("remove_from_inv", i_pos)
                                        DataLoader.change_file("add_to_inv", DataLoader.player_data["armor"][armor_type], i_pos)
                                        DataLoader.change_file("remove_from_armor", armor_type)
                                        DataLoader.change_file("add_to_armor", armor_type, tup[0][1])

                    elif event.button == 4:
                        self.hotbar.change_selected(-1)
                    elif event.button == 5:
                        self.hotbar.change_selected(1)

            # Player movement
            if not self.show_inv and not self.show_menu:
                collided_with_door = self.board.door_collide(self.player)
                collided_with_wall = self.board.wall_collide(self.player)
                if (collided_with_door == "not on door" and not collided_with_wall) or collided_with_door == "door open":
                    if go_right:
                        player_rect = pygame.Rect(
                            self.player.x + mv_amount, self.player.y, self.player.width, self.player.height
                        )
                        if (self.board.door_collide(player_rect) == "not on door" and not self.board.wall_collide(player_rect)) or self.board.door_collide(player_rect) == "door open":
                            if pygame.Rect(self.board.x - mv_amount, self.board.y, self.board.width, self.board.height).contains(display.get_rect()) and mid_screen.collidepoint(self.player.x, self.player.y):
                                self.board.x -= mv_amount
                                for enemy in self.enemies.values():
                                    enemy.x -= mv_amount
                            else:
                                self.player.x += mv_amount
                    if go_left:
                        player_rect = pygame.Rect(
                            self.player.x - mv_amount, self.player.y, self.player.width, self.player.height
                        )
                        if (self.board.door_collide(player_rect) == "not on door" and not self.board.wall_collide(player_rect)) or self.board.door_collide(player_rect) == "door open":
                            if pygame.Rect(self.board.x + mv_amount, self.board.y, self.board.width, self.board.height).contains(display.get_rect()) and mid_screen.collidepoint(self.player.x, self.player.y):
                                self.board.x += mv_amount
                                for enemy in self.enemies.values():
                                    enemy.x += mv_amount
                            else:
                                self.player.x -= mv_amount
                    if go_up:
                        player_rect = pygame.Rect(
                            self.player.x, self.player.y - mv_amount, self.player.width, self.player.height
                        )
                        if (self.board.door_collide(player_rect) == "not on door" and not self.board.wall_collide(player_rect)) or self.board.door_collide(player_rect) == "door open":
                            if pygame.Rect(self.board.x, self.board.y + mv_amount, self.board.width, self.board.height).contains(display.get_rect()) and mid_screen.collidepoint(self.player.x, self.player.y):
                                self.board.y += mv_amount
                                for enemy in self.enemies.values():
                                    enemy.y += mv_amount
                            else:
                                self.player.y -= mv_amount
                    if go_down:
                        player_rect = pygame.Rect(
                            self.player.x, self.player.y + mv_amount, self.player.width, self.player.height
                        )
                        if (self.board.door_collide(player_rect) == "not on door" and not self.board.wall_collide(player_rect)) or self.board.door_collide(player_rect) == "door open":
                            if pygame.Rect(self.board.x, self.board.y - mv_amount, self.board.width, self.board.height).contains(display.get_rect()) and mid_screen.collidepoint(self.player.x, self.player.y):
                                self.board.y -= mv_amount
                                for enemy in self.enemies.values():
                                    enemy.y -= mv_amount
                            else:
                                self.player.y += mv_amount

            # Gets mouse position
            mx, my = pygame.mouse.get_pos()

            # Mouse collision to provide the inspector with data
            if self.show_inv and not self.show_menu:
                inv_collide_data = self.inv_collide(self.inv, *pygame.mouse.get_pos())
                if inv_collide_data is not None:
                    pos, space = inv_collide_data
                    self.name = space[0][1]
                    self.data = {
                        "img": space[0][0],
                        "attr": DataLoader.possible_items[space[0][1]],
                        "inv_pos": pos,
                        "eq_pos": None,
                        "st_pos": None
                    }

                if self.show_equipment:
                    eq_collide_data = self.eq_collide(self.equipment, *pygame.mouse.get_pos())
                    if eq_collide_data is not None:
                        pos, slot = eq_collide_data
                        self.name = slot[0][1]
                        self.data = {
                            "img": slot[0][0],
                            "attr": DataLoader.possible_items[slot[0][1]],
                            "eq_pos": pos,
                            "inv_pos": None,
                            "st_pos": None
                        }
            if self.show_st and not self.show_menu:
                st_collide_data = self.st_collide(self.st, *pygame.mouse.get_pos())
                if st_collide_data is not None:
                    skill, rect, img = st_collide_data
                    self.name = skill["elem"].tag
                    self.data = {
                        "img": img,
                        "attr": {**skill["elem"].attrib, "level": DataLoader.player_data["skills"].get(self.name)},
                        "eq_pos": None,
                        "inv_pos": None,
                        "st_pos": rect
                    }

            player_cell_y, player_cell_x = self.board.cell_collide(self.player)
            player_puz_x, player_puz_y = self.display.maze.cell_table[player_cell_x, player_cell_y]

            # Item drop pickup
            for it_dr_pos, it_dr in enumerate(self.item_drops):
                player_rect = pygame.Rect(
                    self.player.x - self.board.x, self.player.y - self.board.y, self.player.width, self.player.height
                )
                item_rect = pygame.Rect(it_dr.x, it_dr.y, it_dr.width, it_dr.height)
                if player_rect.colliderect(item_rect):
                    next_slot = DataLoader.get_next_open_inv_slot()
                    if next_slot is not None:
                        DataLoader.change_file("remove_from_inv", next_slot)
                        DataLoader.change_file("add_to_inv", it_dr.item.name, next_slot)
                        self.item_drop_display.add_item(
                            (it_dr.item.name, pygame.image.load(MAIN_ASSET_PATH + it_dr.item.name + ".png"))
                        )
                        del self.item_drops[it_dr_pos]

            if not self.show_menu:
                for button, pressed in enumerate(pygame.mouse.get_pressed()):
                    if button == 0 and pressed == 1:
                        cur_item = DataLoader.possible_items[self.hotbar[self.hotbar.selected_pos][1]]
                        if not self.show_inv and not self.show_st:
                            if cur_item.get("melee_speed") is not None:
                                speed = cur_item["melee_speed"]
                                if self.player.melee_cooldown >= (60 * (1 - (speed / 100))):
                                    self.player.melee_cooldown = 0
                                    self.melee_swing.swing = True
                                    self.melee_swing.swing_pos = pygame.mouse.get_pos()

                            elif cur_item.get("proj_dist") is not None:
                                if cur_item.get("mana_used") is not None:
                                    if self.player.mana - cur_item["mana_used"] >= 0:
                                        # player.mana -= cur_item["mana_used"]
                                        self.bullets[self.player_name][self.next_bullet_index] = Bullet(
                                                abs(self.board.x) + self.player.x + self.player.width,
                                                abs(self.board.y) + self.player.y + self.player.height,
                                                abs(self.board.x) + mx,
                                                abs(self.board.y) + my,
                                                cur_item
                                        )
                                        self.next_bullet_index += 1
                                else:
                                    # Arrow
                                    pass

                if self.melee_swing.swing and self.melee_swing.left > 0 and self.melee_swing.right > 0:
                    damage = DataLoader.possible_items[self.hotbar[self.hotbar.selected_pos][1]]["damage"]
                    melee_swing_coords = self.melee_swing.get_coords()
                    for e in self.enemies.values():
                        enemy_lines = self.get_rect_corners(
                            pygame.Rect(e.x + (e.width // 2), e.y + (e.height // 2), e.width, e.height)
                        )
                        hits = [
                            line_collide(melee_swing_coords, (*enemy_lines[a], *enemy_lines[b]))
                            for a, b in zip(range(4), [1, 2, 3, 0])
                        ]
                        if any(hits):
                            e.health -= damage
                            print(e.health)

            # Kill enemy if health < 1
            for ind, e in list(self.enemies.items()):
                if e.health < 1:
                    edrps = self.kill_enemy(self.enemies, ind, self.board, self.item_drops)
                    if edrps is not None:
                        self.item_drops = edrps

            self.player.melee_cooldown += 1

            # Fill the display with black to draw on top of
            self.display.fill((0, 0, 0))

            # Update board surface
            self.board.update()

            # Draw item drops to screen
            for it_dr in self.item_drops:
                it_dr.update()
                self.board.blit(it_dr, (it_dr.x, it_dr.y))

            # Update enemies
            if not self.show_menu or not self.is_singleplayer:
                for enemy in list(self.enemies.values()):
                    l_enemy_pos = [(i.x, i.y) for i in self.enemies.values() if isinstance(i, LargeEnemy)]

                    if self.is_host:
                        r, c = self.board.cell_collide(enemy)
                        puz_x, puz_y = self.display.maze.cell_table[c, r]
                    else:
                        puz_x, puz_y = None, None

                    if isinstance(enemy, LargeEnemy):
                        enemy.l_enemy_pos = l_enemy_pos
                        for se in enemy.spawned_enemies:
                            self.enemies[self.next_enemy_index] = se
                            self.next_enemy_index += 1
                        enemy.spawned_enemies = []

                        sml_enemies = [
                            (i.x + i.width - self.board.x, i.y + i.height - self.board.y)
                            for i in self.enemies.values() if isinstance(i, SmallEnemy) and i.origin == 1
                        ]
                        enemy.bezier_points = Bezier(
                            [(enemy.x + enemy.width - self.board.x, enemy.y + enemy.height - self.board.y)] +
                            sml_enemies[:len(sml_enemies) if len(sml_enemies) < 4 else 4] +
                            [(self.player.x + self.player.width - self.board.x, self.player.y + self.player.height - self.board.y)], 1000
                        ).get_points_c()

                        if enemy.bezier_points:
                            for point in enemy.bezier_points:
                                pygame.draw.circle(self.board, BEZIER_POINT_COLOUR, point, 2)

                    enemy.update(
                        self.player, (puz_x, puz_y), (player_puz_x, player_puz_y), self.display.maze.cell_table, self.board
                    )

                    if isinstance(enemy, MediumEnemy):
                        for b in enemy.bullets:
                            # Uses player name to add bullets to because only the host can spawn enemy bullets
                            self.bullets[self.player_name][self.next_bullet_index] = b
                            self.next_bullet_index += 1
                        enemy.bullets = []

            # Draw bullets to screen
            if not self.show_menu or not self.is_singleplayer:
                for name in self.bullets:
                    for bp, bullet in list(self.bullets[name].items()):
                        bullet_collided = self.bullet_collide(bullet, self.board, self.player, self.enemies)
                        if isinstance(bullet, Bullet):
                            if bullet_collided:
                                bullet.moving = False
                            if bullet.moving:
                                bullet.update(delta_time_scalar)
                                pygame.draw.rect(self.board, bullet.colour, bullet)
                            else:
                                del self.bullets[name][bp]
                        else:
                            pygame.draw.rect(self.board, bullet.colour, bullet)
                            if bullet_collided:
                                del self.bullets[name][bp]

            # Draw other players to the screen
            for op in list(self.other_players.values()):
                op.update(*pygame.mouse.get_pos())
                self.board.blit(op, (op.x, op.y))

            # Draw board to screen
            self.display.blit(self.board, (self.board.x, self.board.y))

            # Draw enemies to screen
            for enemy in self.enemies.values():
                self.display.blit(enemy, (enemy.x, enemy.y))

            # Draw player to screen
            mx, my = pygame.mouse.get_pos()
            self.player.update(mx, my)
            self.display.blit(self.player, (self.player.x, self.player.y))

            # Draw melee swing to screen
            if self.hotbar[self.hotbar.selected_pos][1] != self.melee_swing.item:
                self.melee_swing = MeleeSwing(self.player, self.hotbar[self.hotbar.selected_pos][1])
            self.melee_swing.update()
            p_rect = pygame.Rect(
                self.player.x + (self.player.width // 2),
                self.player.y + (self.player.height // 2),
                self.player.width,
                self.player.height
            )
            self.melee_swing.x = p_rect.centerx - (self.melee_swing.width // 2)
            self.melee_swing.y = p_rect.centery - (self.melee_swing.height // 2)
            self.display.blit(self.melee_swing, (self.melee_swing.x, self.melee_swing.y))

            # Send network data
            if not self.is_host and not self.is_singleplayer:
                self.client.send(json.dumps({"request": "GET DATA", "payload": self.client.load_json()}).encode())

            # Update hotbar surface and draw to screen
            self.hotbar.update()
            self.display.blit(
                self.hotbar, (self.display.width // 3, self.display.height - self.hotbar.height)
            )

            # Update health bar surface and draw to screen
            healthbar.update(self.font, self.player.health)
            self.display.blit(
                healthbar,
                (
                    self.display.width // 20,
                    self.display.height - (self.hotbar.height - self.hotbar.height // 4)
                )
            )

            # Update mana bar surface and draw to screen
            manabar.update(self.font, self.player.mana)
            self.display.blit(
                manabar,
                (
                    (self.display.width // 20) * 15,
                    self.display.height - (self.hotbar.height - self.hotbar.height // 4)
                )
            )

            # Update item drop display and draw to screen
            self.item_drop_display.update(self.font)
            self.display.blit(
                self.item_drop_display,
                (
                    self.display.width - self.item_drop_display.width,
                    self.display.height // 2 - (self.item_drop_display.height // 1.5)
                )
            )

            # Update inventory surface and draw to screen
            if self.show_inv:
                self.inv.update(self.data)
                self.display.blit(
                    self.inv,
                    (
                        self.display.width // 2 - (self.inv.width // 2),
                        self.display.height // 2 - (self.inv.height // 2)
                    )
                )

            # Update inspector if inventory or skill tree is open
            if self.show_inv or self.show_st:
                self.inspector.update(self.name, self.font, self.data)
                self.display.blit(
                    self.inspector,
                    (
                        self.display.width - self.inspector.width,
                        self.display.height // 2 - (self.inspector.height // 2)
                    )
                )

            # Update equipment if inventory is open and equipment is selected
            if self.show_inv and self.show_equipment:
                self.equipment.update(self.font, self.data)
                self.display.blit(
                    self.equipment,
                    (
                        0,
                        self.display.height // 2 - (self.equipment.height // 2)
                    )
                )

            # Update attributes if inventory is open and attributes is selected
            if self.show_inv and not self.show_equipment:
                self.attributes.update(self.font)
                self.display.blit(
                    self.attributes,
                    (
                        0,
                        self.display.height // 2 - (self.attributes.height // 2)
                    )
                )

            # Update tab if inventory is open
            if self.show_inv:
                self.tab.update(self.font)
                self.display.blit(
                    self.tab,
                    (
                        0,
                        self.display.height // 2 - (self.attributes.height // 2)
                    )
                )

            # Update XP bar if inventory is open
            if self.show_inv:
                self.xp_bar.update(self.font)
                self.display.blit(
                    self.xp_bar,
                    (
                        self.display.width // 2 - (self.inv.width // 2),
                        self.display.height // 2 - (self.inv.height // 2) - self.xp_bar.height
                    )
                )

            # Update skill tree surface
            if self.show_st:
                self.st.update(self.font, self.data)
                self.display.blit(
                    self.st,
                    (
                        0,
                        self.display.height // 2 - (self.st.height // 2)
                    )
                )

            # Pause menu
            if self.show_menu:
                self.display.pause_menu.update(self.font, *pygame.mouse.get_pos())
                self.display.blit(
                    self.display.pause_menu,
                    (
                        self.display.pause_menu.x,
                        self.display.pause_menu.y
                    )
                )

            # Draw fps counter
            fps_txt = self.font.render(str(round(clock.get_fps(), 0)), True, (0, 255, 0))
            self.display.blit(fps_txt, (0, 0))

            # Draw display to window
            window.blit(display, (0, 0))

            # Update whole screen
            pygame.display.update()
        # TODO: Close the server properly
        # if self.is_host and not self.is_singleplayer:
        #     self.game_server.sock.shutdown(socket.SHUT_RDWR)
        #     self.game_server.sock.close()
        if not self.is_host and not self.is_singleplayer:
            self.client.sock.close()


display = Display(width, height)
game = None
multiplayer_game_menu = None
game_on = True
start_single_game = False
start_screen = True
join_multiplayer_pressed = False
loaded_servers = False
svr_addr = ""
start_multiplayer_game = False
join_multiplayer_game = False
character_selected = None
start_menu_font = pygame.font.SysFont("Courier", 15, True)
title_font = pygame.font.SysFont("Courier", 50, True)
title_text = title_font.render(GAME_TITLE, True, TEXT_COLOUR)
title_size = title_font.size(GAME_TITLE)
select_menu_font = pygame.font.SysFont("Courier", 20, True)
while game_on:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_on = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                join_multiplayer_pressed = False
                start_screen = True
                loaded_servers = False
            if event.key == pygame.K_LEFT:
                if join_multiplayer_pressed:
                    multiplayer_game_menu.current_page -= 1
            if event.key == pygame.K_RIGHT:
                if join_multiplayer_pressed:
                    multiplayer_game_menu.current_page += 1
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if start_screen:
                    display.start_menu.check_pressed(*pygame.mouse.get_pos())
                    display.character_menu.check_pressed(*pygame.mouse.get_pos())
                if join_multiplayer_pressed:
                    if multiplayer_game_menu is not None:
                        multiplayer_game_menu.check_pressed(*pygame.mouse.get_pos())

    window.fill((0, 0, 0))

    if start_screen:
        display.start_menu.update(start_menu_font, *pygame.mouse.get_pos())
        window.blit(display.start_menu, (display.start_menu.x, display.start_menu.y))
        display.character_menu.update(start_menu_font, *pygame.mouse.get_pos(), character_selected)
        window.blit(display.character_menu, (display.character_menu.x, display.character_menu.y))
        window.blit(title_text, ((WINDOW_WIDTH // 2) - (title_size[0] // 2), 0))

    if start_single_game:
        game = Game(display, True, True, character_selected)
        window.blit(display, (0, 0))
        game.start()

    if start_multiplayer_game:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((GNS_IP, GNS_PORT))
            process = subprocess.run(["ipconfig"], stdout=subprocess.PIPE)
            out = process.stdout.decode()
            ipv4 = out[out.find("IPv4"):][out[out.find("IPv4"):].find("1"):out[out.find("IPv4"):].find("\r")]
            port = randint(GNS_PORT + 1, 55000)
            req = {
                "request": "HOST ADD",
                "payload": {"name": "test game 1", "password": "test password", "address": f"{ipv4}:{port}"}
            }
            s.send(json.dumps(req).encode())
            game = Game(display, True, False, character_selected, server_ip=ipv4, server_port=port)
            window.blit(display, (0, 0))
            game.start()
            req = {
                "request": "HOST REMOVE",
                "payload": req["payload"]
            }
            s.send(json.dumps(req).encode())
            s.close()
        except ConnectionRefusedError:
            print("GNS not on")
            start_multiplayer_game = False

    if join_multiplayer_game:
        game = Game(display, False, False, character_selected, host_address=svr_addr)
        window.blit(display, (0, 0))
        game.start()

    if join_multiplayer_pressed:
        if not loaded_servers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((GNS_IP, GNS_PORT))
                req = {"request": "GET ALL SERVERS", "payload": {}}
                s.send(json.dumps(req).encode())
                data = json.loads(s.recv(2048).decode())
                s.close()
                if data:
                    multiplayer_game_menu = SelectMenu(WINDOW_WIDTH // 2 - (SELECT_MENU_WIDTH // 2), WINDOW_HEIGHT // 2 - (SELECT_MENU_HEIGHT // 2), [
                        (
                            (i["name"], i["address"]),
                            lambda: exec(f"svr_addr = '{i['address']}'; join_multiplayer_pressed = False; join_multiplayer_game = True; loaded_servers = False", globals())
                        ) for i in data
                    ])
                    loaded_servers = True
                    start_screen = False
                else:
                    print("No servers on")
                    join_multiplayer_pressed = False
            except ConnectionRefusedError:
                print("GNS not on")
                join_multiplayer_pressed = False
        else:
            window.blit(multiplayer_game_menu, (multiplayer_game_menu.x, multiplayer_game_menu.y))
            multiplayer_game_menu.update(select_menu_font, *pygame.mouse.get_pos())

    pygame.display.update()
    clock.tick(30)

pygame.quit()

