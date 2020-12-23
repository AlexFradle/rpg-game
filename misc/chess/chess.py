import pygame
from PIL import Image

pygame.init()


class Board(pygame.Surface):
    def __init__(self, w, h, g):
        super().__init__((w, h), pygame.SRCALPHA)
        self.grid = g
        sq_w, sq_h = w // 8, h // 8
        self.squares = [
            [[pygame.Rect(j * sq_w, i * sq_h, sq_w, sq_h), "dark" if (i + 1) % 2 == 0 else "light"] for j in range(len(self.grid[0]))]
            for i in range(len(self.grid))
        ]
        for r in range(len(self.squares)):
            for s in range(len(self.squares[0])):
                self.squares[r][s][1] = self.squares[(r + 1) if r < len(self.squares) - 1 else 1][s][1] if (s + 1) % 2 == 0 else self.squares[r][s][1]

        self.imgs = {}
        for i in ["w_king.png", "w_queen.png", "w_rook.png", "w_bishop.png", "w_knight.png", "w_pawn.png",
                  "b_king.png", "b_queen.png", "b_rook.png", "b_bishop.png", "b_knight.png", "b_pawn.png"]:

            if i in ["w_knight.png", "b_knight.png"]:
                k = i[0] + "N"
                self.imgs[k] = pygame.image.load(i)
            else:
                k = i[0] + i.replace("_", "")[1:2].upper()
                self.imgs[k] = pygame.image.load(i)

    def update(self, grid):
        self.fill((0, 0, 0))
        self.grid = grid
        for sq_row, g_row in zip(self.squares, self.grid):
            for sq, g in zip(sq_row, g_row):
                pygame.draw.rect(self, (209, 139, 71) if sq[1] == "dark" else (255, 206, 158), sq[0])
                if g in self.imgs.keys():
                    self.blit(self.imgs[g], (sq[0].x, sq[0].y))


class Piece:
    def __init__(self, name: str, colour: str, x: str, y: str):
        self.name = name
        self.colour = colour
        self.x = x
        self.y = y


class Pawn(Piece):
    def __init__(self, name, colour, x, y):
        super().__init__(name, colour, x, y)

    def check_move(self, x, y):
        pass


window = pygame.display.set_mode((1280, 800), pygame.SRCALPHA)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier", 15, True)

# White at the bottom
start_grid = [
    ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
    ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " ", " ", " ", " "],
    ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
    ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
]
char_to_int = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8}

board = Board(800, 800, start_grid)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pass

    window.fill((0, 0, 0))

    board.update(start_grid)
    window.blit(board, (0, 0))

    pygame.display.update()
    clock.tick(60)

pygame.quit()

# for i in [
#     "w_king.png", "w_queen.png", "w_rook.png", "w_bishop.png", "w_knight.png", "w_pawn.png",
#     "b_king.png", "b_queen.png", "b_rook.png", "b_bishop.png", "b_knight.png", "b_pawn.png",
# ]:
#     im = Image.open(f"raw_imgs/{i}")
#     resized = im.resize((100, 100))
#     resized.save(i)


