import pygame
pygame.init()


class Snake(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20)
        self.body = []
        self.past_pos = []

    def move_(self, x_amount, y_amount):
        self.past_pos.append((self.x, self.y))
        self.x += x_amount
        self.y += y_amount

    def add_body(self):
        self.body.append(Body(*self.past_pos[-(len(self.body) + 1)]))

    def update(self):
        for pos, b in enumerate(self.body):
            b.x, b.y = self.past_pos[-(pos + 1)]
        del self.past_pos[:-(len(self.body) + 1)]


class Body(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20)


width, height = 1280, 720
display = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

mv_amount = 20
x_amount = mv_amount
y_amount = 0

snake = Snake(20, 20)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                snake.add_body()

            elif event.key == pygame.K_d:
                x_amount = mv_amount
                y_amount = 0
            elif event.key == pygame.K_a:
                x_amount = -mv_amount
                y_amount = 0
            elif event.key == pygame.K_w:
                x_amount = 0
                y_amount = -mv_amount
            elif event.key == pygame.K_s:
                x_amount = 0
                y_amount = mv_amount

    snake.move_(x_amount, y_amount)
    snake.update()

    display.fill((0, 0, 0))

    pygame.draw.rect(display, (0, 255, 0), snake)

    for sect in snake.body:
        pygame.draw.rect(display, (255, 255, 255), sect)

    pygame.display.update()
    clock.tick(20)

pygame.quit()
