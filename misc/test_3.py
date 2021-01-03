# import pygame
# pygame.init()
#
# WINDOW_WIDTH = 1280
# WINDOW_HEIGHT = 720
#
#
# class MessageBox(pygame.Surface):
#     def __init__(self, txt: str, background: tuple):
#         self.__width = WINDOW_WIDTH // 1.1
#         self.__height = WINDOW_HEIGHT // 6
#         super().__init__((self.__width, self.__height), pygame.SRCALPHA)
#         self.__txt = txt
#         margin_x = 10
#         margin_y = 10
#         self.__inner_box = pygame.Rect(margin_x, margin_y, self.__width - margin_x*2, self.__height - margin_y*2)
#         self.__background = background
#         button_width = self.__width // 10
#         button_height = self.__height // 4
#         self.__button = pygame.Rect(
#             (self.__width // 2) - (button_width // 2),
#             self.__height - button_height - margin_y*2,
#             button_width, button_height
#         )
#
#     @property
#     def width(self):
#         return self.__width
#
#     @property
#     def height(self):
#         return self.__height
#
#     def check_pressed(self, mx: int, my: int):
#         if self.__button.collidepoint(mx, my):
#             exec("message_popup = True", globals())
#
#     def update(self, font):
#         self.fill((60, 60, 60, 60))
#         pygame.draw.rect(self, self.__background, self.__inner_box)
#         pygame.draw.rect(self, (255, 255, 255), self.__button)
#         txt = font.render(self.__txt, True, (255, 255, 255))
#         self.blit(
#             txt,
#             ((self.__width // 2) - (font.size(self.__txt)[0] // 2), (self.__height // 2) - (font.size(self.__txt)[1] // 2))
#         )
#         button_txt = font.render("EXIT", True, (0, 0, 0))
#         self.blit(
#             button_txt,
#             ((self.__width // 2) - (font.size("EXIT")[0] // 2), (self.__button.y + (self.__button.h // 2)) - (font.size("EXIT")[1] // 2))
#         )
#
#
# display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
# clock = pygame.time.Clock()
# font = pygame.font.SysFont("courier", 15, True)
#
# msg = MessageBox("All of the team is dead. You survived until ROUND 11", (255, 0, 0))
#
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#
#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_ESCAPE:
#                 running = False
#
#     display.fill((0, 0, 0))
#
#     msg.update(font)
#     display.blit(msg, ((WINDOW_WIDTH // 2) - (msg.width // 2), (WINDOW_HEIGHT // 2) - (msg.height // 2)))
#
#     pygame.display.update()
#     clock.tick(60)

import webbrowser
from os import getcwd

cwd = getcwd().replace("\\", "/") + "/"

# webbrowser.open(f"file//{cwd}help.html", new=2)
webbrowser.open(f"https://www.google.com", new=2)
