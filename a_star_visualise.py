import pygame
from a_star import AStar
from random import randint
pygame.init()


class Space(pygame.Rect):
    def __init__(self, x, y, w, h, wall):
        super().__init__(x, y, w, h)
        self.wall = wall
        self.path = False
        self.end = False
        self.start = False
        self.checked = False


width, height = 1024, 720
display = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

font = pygame.font.SysFont("Courier", 15, True)
running = True
drawing = False
cont_solve = False
animation = True
rect_width = 0

grid_w, grid_h = 51, 35
grid = [[Space(20 * j, 20 * i, 20, 20, True if randint(1, 100) < 30 else False) for j in range(grid_w)] for i in range(grid_h)]
drawn_spaces = []
checked = []


def solve():
    global cont_solve, animation, drawn_spaces, checked
    file = "\n".join(
        ["".join(["e" if s.end else ("s" if s.start else ("#" if s.wall else " ")) for s in row]) for row in grid])
    with open("maze.txt", "w") as f:
        f.write(file)
    a = AStar(grid_w, grid_h, True, False)
    path, checked = a.solve()
    for row in grid:
        for cell in row:
            cell.path = False
            cell.checked = False
    if path is not None:
        cont_solve = True
        drawn_spaces = []
        for p in path:
            grid[p.y][p.x].path = True
        for c in checked:
            try:
                grid[c.y][c.x].checked = True
            except Exception as e:
                print(e, c.x, c.y)
    else:
        print("NOT SOLVEABLE")


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True

        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False

        if event.type == pygame.KEYDOWN:
            # Quits game
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_UP:
                rect_width += 1
            elif event.key == pygame.K_DOWN:
                rect_width -= 1
            elif event.key == pygame.K_RETURN:
                solve()
            elif event.key == pygame.K_r:
                grid = [[Space(20 * j, 20 * i, 20, 20, False) for j in range(grid_w)]
                        for i in range(grid_h)]
                cont_solve = False
            elif event.key == pygame.K_e:
                mx, my = pygame.mouse.get_pos()
                for row in grid:
                    for space in row:
                        if space.collidepoint(mx, my):
                            space.end = not space.end
            elif event.key == pygame.K_s:
                mx, my = pygame.mouse.get_pos()
                for row in grid:
                    for space in row:
                        if space.collidepoint(mx, my):
                            space.start = not space.start

    if drawing:
        mx, my = pygame.mouse.get_pos()
        for row in grid:
            for space in row:
                if space.collidepoint(mx, my):
                    # space.wall = not space.wall
                    space.wall = True

    if cont_solve and not animation:
        solve()

    display.fill((0, 0, 0))

    if animation:
        if checked:
            drawn_spaces.append((checked[0].x, checked[0].y))
            checked.pop(0)
        for r_pos, row in enumerate(grid):
            for s_pos, space in enumerate(row):
                if (s_pos, r_pos) in drawn_spaces:
                    col = (0, 255, 0) if space.path else ((0, 0, 0) if space.wall else ((255, 0, 0) if space.end else ((0, 0, 255) if space.start else ((0, 128, 255) if space.checked else (255, 255, 255)))))
                    pygame.draw.rect(display, col, space, rect_width)
                else:
                    col = (0, 0, 0) if space.wall else ((255, 0, 0) if space.end else ((0, 0, 255) if space.start else (255, 255, 255)))
                    pygame.draw.rect(display, col, space, rect_width)
    else:
        for row in grid:
            for space in row:
                col = (0, 255, 0) if space.path else ((0, 0, 0) if space.wall else ((255, 0, 0) if space.end else ((0, 0, 255) if space.start else ((0, 128, 255) if space.checked else (255, 255, 255)))))
                pygame.draw.rect(display, col, space, rect_width)

    pygame.display.update()
    clock.tick(200)

pygame.quit()


