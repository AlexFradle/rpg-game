# import socket
# import json
#
# test_req = {"request": "HOST ADD", "payload": {"name": "test game 2", "password": "test password"}}
# # test_req = {"request": "GET ALL SERVERS", "payload": {}}
#
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect(("192.168.1.103", 50000))
# s.send(json.dumps(test_req).encode())
# while True:
#     a = input(">>>")
#     if a == "e":
#         break
# s.close()

# import hashlib
#
# password = hashlib.sha256(b"test password 123 !#/").hexdigest()
#
# test = input("Enter password: ").encode()
#
# if password == hashlib.sha256(test).hexdigest():
#     print(password)

import pygame
from string import ascii_lowercase

pygame.init()
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
CLASS_NAMES = ["mage", "warrior", "archer", "looter"]


class CharacterCreator(pygame.Surface):
    def __init__(self):
        super().__init__((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), pygame.SRCALPHA)
        self.__width = WINDOW_WIDTH // 2
        self.__height = WINDOW_HEIGHT // 2
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

    def add_char(self, char: str) -> None:
        if len(self.__name) < 21:
            self.__name += char

    def remove_char(self) -> None:
        if len(self.__name) > 0:
            self.__name = self.__name[:-1]

    def check_pressed(self, mx, my):
        for pos, cr in enumerate(self.__class_rects):
            if cr.collidepoint(mx, my):
                self.__selected_class = CLASS_NAMES[pos]

    def update(self, font, mx, my):
        self.fill((60, 60, 60, 60))
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


window = pygame.display.set_mode((1280, 800), pygame.SRCALPHA)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier", 15, True)

cc = CharacterCreator()

running = True
while running:
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_BACKSPACE:
                cc.remove_char()
            for asc, pressed in enumerate(pygame.key.get_pressed()):
                if pressed and chr(asc).lower() in ascii_lowercase:
                    cc.add_char(chr(asc).lower())
                    break
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                cc.check_pressed(mx - 100, my - 100)

    window.fill((0, 0, 0))

    cc.update(font, mx - 100, my - 100)
    window.blit(cc, (100, 100))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
