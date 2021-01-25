import pygame
import math

pygame.init()
display = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
running = True
MAX_MELEE_SWING_WIDTH = 400
MAX_MELEE_SWING_HEIGHT = 400
fps = 30


def line_collide(line_1_coords, line_2_coords):
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


class Player:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class MeleeSwing(pygame.Surface):
    """Surface which the melee swing animation is drawn to"""
    def __init__(self, owner: Player, item: str):
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


player = Player(360, 360, 40, 40)
melee_swing = MeleeSwing(player, "")
enemy_rect = pygame.Rect(100, 100, 50, 50)
start = False

while running:
    ms = clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                melee_swing.swing_pos = pygame.mouse.get_pos()
                melee_swing.swing = True
                start = True
            if event.button == 3:
                mx, my = pygame.mouse.get_pos()
                enemy_rect.x = mx
                enemy_rect.y = my

    display.fill((0, 0, 0))

    melee_swing.update()
    p_rect = pygame.Rect(player.x + (player.width // 2), player.y + (player.height // 2), player.width, player.height)
    melee_swing.x = p_rect.centerx - (melee_swing.width // 2)
    melee_swing.y = p_rect.centery - (melee_swing.height // 2)
    display.blit(melee_swing, (melee_swing.x, melee_swing.y))

    pygame.draw.rect(display, (0, 255, 0), pygame.Rect(player.x, player.y, player.width*2, player.height*2))
    ms_rect = pygame.Rect(melee_swing.x, melee_swing.y, melee_swing.width, melee_swing.height)
    # Calculate coords on melee_swing circle using the equation:
    # (x, y) = (cx + (r * cos(angle)), cy - (r * sin(angle)))
    #                                     ^
    #                        Inverted y due to inverted axis
    melee_swing_coords = (
        ms_rect.centerx + ((melee_swing.width // 2) * math.cos(melee_swing.left)),
        ms_rect.centery - ((melee_swing.width // 2) * math.sin(melee_swing.left)),
        ms_rect.centerx + ((melee_swing.width // 2) * math.cos(melee_swing.right)),
        ms_rect.centery - ((melee_swing.width // 2) * math.sin(melee_swing.right))
    )
    pygame.draw.rect(display, (255, 0, 0), enemy_rect, 2)

    pygame.draw.line(display, (0, 128, 255), (melee_swing_coords[0], melee_swing_coords[1]), (melee_swing_coords[2], melee_swing_coords[3]))

    if start:
        rect_lines = get_rect_corners(enemy_rect)
        collision = [line_collide((*rect_lines[i], *rect_lines[j]), melee_swing_coords) for i, j in zip([0, 1, 2, 3], [1, 2, 3, 0])]
        for i in collision:
            if i:
                pygame.draw.circle(display, (0, 0, 255), (int(i[0]), int(i[1])), 7)

    pygame.display.update()

pygame.quit()
