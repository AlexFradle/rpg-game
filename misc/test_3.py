import pygame
pygame.init()

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
SELECT_MENU_WIDTH = 800
SELECT_MENU_HEIGHT = 600
SELECT_MENU_BACKGROUND_COLOUR = (60, 60, 60, 60)
SELECT_MENU_MARGIN_X = 50
SELECT_MENU_MARGIN_Y = 20
SELECT_MENU_BUTTON_COLOUR = (255, 128, 0)
TEXT_COLOUR = (255, 255, 255)
SELECT_MENU_SELECTED = (255, 255, 255)


class SelectMenu(pygame.Surface):
    def __init__(self, buttons):
        super().__init__((SELECT_MENU_WIDTH, SELECT_MENU_HEIGHT), pygame.SRCALPHA)
        self.__x = WINDOW_WIDTH // 2 - (SELECT_MENU_WIDTH // 2)
        self.__y = WINDOW_HEIGHT // 2 - (SELECT_MENU_HEIGHT // 2)
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
    def current_page(self, value):
        self.__current_page = value if 0 <= value < len(self.__buttons) else self.__current_page

    def check_pressed(self, mx, my, flag=1):
        for b, bp in zip(self.__buttons[self.__current_page], self.__button_pos):
            if pygame.Rect(bp.x + self.__x, bp.y + self.__y, bp.w, bp.h).collidepoint(mx, my):
                if flag == 1:
                    b[1]()
                else:
                    return bp

    def update(self, font, mx, my):
        self.fill(SELECT_MENU_BACKGROUND_COLOUR)
        focused_rect = self.check_pressed(mx, my, 2)
        pygame.draw.rect(self, SELECT_MENU_BUTTON_COLOUR, self.__left_button)
        pygame.draw.rect(self, SELECT_MENU_BUTTON_COLOUR, self.__right_button)
        left_arrow = font.render("<-", True, TEXT_COLOUR)
        right_arrow = font.render("->", True, TEXT_COLOUR)
        self.blit(left_arrow, (self.__left_button.x, self.__left_button.y))
        self.blit(right_arrow, (self.__right_button.x, self.__right_button.y))
        for b, bp in zip(self.__buttons[self.__current_page], self.__button_pos):
            pygame.draw.rect(self, SELECT_MENU_BUTTON_COLOUR, bp)
            if bp == focused_rect:
                pygame.draw.rect(self, SELECT_MENU_SELECTED, bp, 4)
            main_txt = font.render(b[0][0], True, TEXT_COLOUR)
            second_txt = font.render(b[0][1], True, TEXT_COLOUR)
            self.blit(main_txt, (bp.x, bp.y))
            self.blit(second_txt, (bp.x + bp.w - font.size(b[0][1])[0], bp.y))
            if len(b[0]) > 2:
                third_txt = font.render(b[0][2], True, TEXT_COLOUR)
                self.blit(third_txt, (bp.x, bp.y + bp.h - font.size(b[0][2])[1]))


display = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
font = pygame.font.SysFont("Courier", 20, True)
sm = SelectMenu([
    (("Test game 1", "192.168.1.103:51230"), lambda: exec("")),
    (("Test game 2", "192.168.1.103:51230"), lambda: exec("")),
    (("Test game 3", "192.168.1.103:51230"), lambda: exec("")),
    (("Test game 4", "192.168.1.103:51230"), lambda: exec("")),
    (("Test game 5", "192.168.1.103:51230"), lambda: exec("")),
    (("Test game 6", "192.168.1.103:51230"), lambda: exec("")),
    (("Test game 7", "192.168.1.103:51230"), lambda: exec("")),
    (("Test game 8", "192.168.1.103:51230"), lambda: exec(""))
])

fps = 60

while running:
    ms = clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_RIGHT:
                sm.current_page += 1
            if event.key == pygame.K_LEFT:
                sm.current_page -= 1
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pass

    display.fill((0, 0, 0))

    display.blit(sm, (sm.x, sm.y))
    sm.update(font, *pygame.mouse.get_pos())

    pygame.display.update()

pygame.quit()
