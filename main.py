import pygame


RESPAWN_PERIOD = 700

pygame.init()
screen = pygame.display.set_mode((1000, 900))
screen.blit(pygame.image.load("img/background.png").convert(), [0, 0])
tanks, run, move_tank, SPEED = [], True, False, 10
time_of_last_shooting = 0
no_coord, fires = [], []
clock = pygame.time.Clock()
clock.tick()

pygame.mixer.init()
background_sound = pygame.mixer.Sound('sound/background.wav')
background_sound.set_volume(0.5)
background_sound.play(-1)

shoot_clock = pygame.time.Clock()

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
        self.alive = True
        self.time_of_last_death = 0
        self.go = 'up'
        self.time_of_last_shooting = 0
        self.player_image = pygame.image.load('img/tank_up.png').convert_alpha()
        screen.blit(self.player_image, self.player_image.get_rect(center=(self.x, self.y)))
        self.paint()

    def move(self, x, y):
        if self.alive:
            if 870 >= self.x + x >= 20 and 870 >= self.y + y >= 20:
                    self.x += x
                    self.y += y
                    self.paint()

    def paint(self):
        screen.blit(self.player_image, self.player_image.get_rect(center=(self.x, self.y)))

    def img(self, name):
        if self.alive:
            if name != 'img/fire.png':
                self.go = name.split('_')[-1][0:-4]
            self.player_image = pygame.image.load(name).convert_alpha()
        if 'bang' in name:
            self.player_image = pygame.image.load(name).convert_alpha()

    def fire(self):
        if self.alive:
            BULLET_SPEED = 20
            SHOOT_PERIOD = 500
            if not pygame.time.get_ticks() - self.time_of_last_shooting >= SHOOT_PERIOD:
                return
            if self.go == 'up':
                x, y = 0, -BULLET_SPEED
            elif self.go == 'down':
                x, y = 0, BULLET_SPEED
            elif self.go == 'left':
                x, y = -BULLET_SPEED, 0
            elif self.go == 'right':
                x, y = BULLET_SPEED, 0
            ball = Bullet(self.x, self.y, x, y, len(fires))
            fires.append(ball)
            self.time_of_last_shooting = pygame.time.get_ticks()
            pygame.mixer.Sound('sound/shoot.wav').play()

    def die(self):
        if self.alive:
            self.alive = False
            self.time_of_last_death = pygame.time.get_ticks()
            pygame.mixer.Sound('sound/hit.wav').play()
            self.respawn()

    def respawn(self):
        time_from_death = pygame.time.get_ticks() - self.time_of_last_death
        if time_from_death >= RESPAWN_PERIOD:
            self.alive = True
            player.img('img/tank_' + self.go + '.png')
            return
        # set frame
        frame_num = time_from_death // (RESPAWN_PERIOD // 7)
        if frame_num == 0:
            frame_num = 1
        self.img('img/bang/kill' + str(frame_num) + '.png')


class Bullet:
    def __init__(self, x, y, nx, ny, ind):
        OFFSET = -3.1  # aligns bullet
        self.flew = False
        self.x, self.y, self.nx, self.ny, self.ind = x + OFFSET, y + OFFSET, nx, ny, ind
        self.player_image = pygame.image.load('img/bullet.png').convert_alpha()

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
        self.time_of_last_death = 0
        self.nx, self.ny = 0, 5
        self.go = 'down'
        self.alive = True
        self.time_of_last_shooting = 0
        self.player_image = pygame.image.load('img/enemy_down.png').convert_alpha()
        self.paint()


player = Player((450, 450))
enemy = Enemy(100, 100)
pygame.time.set_timer(1, 500)
while run:
    screen.blit(pygame.image.load("img/background.png").convert(), [0, 0])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:
                enemy.fire()

            if event.key == pygame.K_QUOTE:
                player.fire()

        elif event.type == 2:
            pygame.time.set_timer(1, 0)
            pygame.time.set_timer(2, 1000)

    for fire in fires:
        fire.growth()

        # check kills
        size_x, size_y = enemy.player_image.get_size()
        killed_enemy = enemy.x - size_x // 2 <= fire.x <= enemy.x + size_x // 2 and enemy.y - size_y // 2 <= fire.y <= enemy.y + size_y // 2

        size_x, size_y = player.player_image.get_size()
        killed_player = player.x - size_x // 2 <= fire.x <= player.x + size_x // 2 and player.y - size_y // 2 <= fire.y <= player.y + size_y // 2

        # check: did the fire flew from tank
        if not fire.flew and (killed_player or killed_enemy):
            continue
        else:
            fire.flew = True

        if killed_enemy:
            index = fires.index(fire)
            fires.pop(index)
            enemy.die()
        if killed_player:
            index = fires.index(fire)
            fires.pop(index)
            player.die()

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

    if keys[pygame.K_a]:
        enemy.img('img/enemy_left.png')
        enemy.move(-SPEED, 0)

    elif keys[pygame.K_d]:
        enemy.img('img/enemy_right.png')
        enemy.move(SPEED, 0)

    elif keys[pygame.K_w]:
        enemy.img('img/enemy_up.png')
        enemy.move(0, -SPEED)

    elif keys[pygame.K_s]:
        enemy.img('img/enemy_down.png')
        enemy.move(0, SPEED)

    if not enemy.alive:
        enemy.respawn()
    if not player.alive:
        player.respawn()

    player.paint()
    enemy.paint()
    pygame.display.flip()


pygame.quit()
