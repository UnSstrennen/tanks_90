import pygame

pygame.init()
screen = pygame.display.set_mode((1000, 900))
screen.blit(pygame.image.load("img/background.png").convert(), [0, 0])
tanks, run, move_tank, SPEED = [], True, False, 10
no_coord, fires = [], []
enemys = []
clock = pygame.time.Clock()
clock.tick()
for x in list(range(0, 230)) + list(range(710, 901)):
    n = []
    for y in range(221):
        n.append((x, y))
    for y in range(710, 901):
        n.append((x, y))
    no_coord += n[:]

pygame.display.flip()


class Player:
    def __init__(self, pos):
        self.x, self.y = pos
        self.go = 'up'
        self.player_image = pygame.image.load('img/tank_up.png').convert_alpha()
        screen.blit(self.player_image, self.player_image.get_rect(center=(self.x, self.y)))
        self.paint()

    def move(self, x, y):
        if 870 >= self.x + x >= 20 and 870 >= self.y + y >= 20 and (self.x + x, self.y + y) not in no_coord:
                self.x += x
                self.y += y
                self.paint()

    def paint(self):
        screen.blit(self.player_image, self.player_image.get_rect(center=(self.x, self.y)))

    def img(self, name):
        self.go = name.split('_')[-1][0:-4]
        self.player_image = pygame.image.load(name).convert_alpha()

    def fire(self):
        if self.go == 'up':
            x, y = 0, -5
        elif self.go == 'down':
            x, y = 0, 5
        elif self.go == 'left':
            x, y = -5, 0
        elif self.go == 'right':
            x, y = 5, 0
        ball = Bullet(self.x, self.y, x, y, len(fires))
        fires.append(ball)


class Bullet:
    def __init__(self, x, y, nx, ny, ind):
        self.x, self.y, self.nx, self.ny, self.ind = x, y, nx, ny, ind
        self.player_image = pygame.image.load('img/fire.png').convert_alpha()

    def growth(self):
        self.x += self.nx
        self.y += self.ny
        if 900 >= self.x >= 0 and 900 >= self.y >= 0 and (self.x, self.y) not in no_coord:
            screen.blit(self.player_image, [self.x, self.y])
        else:
            self.clear()

    def clear(self):
        fires.pop(0)


class Enemy(Player):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.nx, self.ny = 0, 5
        self.player_image = pygame.image.load('img/enemy_down.png').convert_alpha()

    def growth(self):
        self.x += self.nx
        self.y += self.ny
        if 900 >= self.x >= 0 and 900 >= self.y >= 0 and (self.x, self.y) not in no_coord:
            screen.blit(self.player_image, [self.x, self.y])
        else:
            self.clear()


player = Player((450, 450))
pygame.time.set_timer(1, 500)
while run:
    screen.blit(pygame.image.load("img/background.png").convert(), [0, 0])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.fire()
        elif event.type == 2:
            enemys.append(Enemy(500, 50))
            pygame.time.set_timer(1, 0)
            pygame.time.set_timer(2, 1000)
    for i in enemys:
        i.growth()

    for fire in fires:
        fire.growth()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.img('img/tank_left.png')
        player.move(-SPEED, 0)

    elif keys[pygame.K_RIGHT]:
        player.img('img/tank_right.png')
        player.move(SPEED, 0)

    elif keys[pygame.K_UP]:
        player.img('img/tank_up.png')
        player.move(0, -SPEED)

    elif keys[pygame.K_DOWN]:
        player.img('img/tank_down.png')
        player.move(0, SPEED)

    player.paint()
    pygame.display.flip()


pygame.quit()
