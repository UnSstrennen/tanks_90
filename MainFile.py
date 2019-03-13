import pygame
from random import randint


RESPAWN_PERIOD, SPEED = 1000, 5
BUFF_PERIOD, MAX_BUFFS, TIME_OF_BUFF_ACTIVITY = 10000, 2, 5000
run, move_tank = True, False
text_end = ''
map_list = []
time_of_last_shooting, fires = 0, []
players = pygame.sprite.Group()
bullets = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
flags = pygame.sprite.Group()
buffs =  pygame.sprite.Group()



pygame.init()
screen = pygame.display.set_mode((900, 900))

pygame.mixer.init()
background_sound = pygame.mixer.Sound('data/sound/background_music.wav')
background_sound.set_volume(0.1)
background_sound.play(-1)

BUFF_ID = 23
pygame.time.set_timer(BUFF_ID, BUFF_PERIOD)

shoot_clock = pygame.time.Clock()
clock = pygame.time.Clock()
clock.tick()
pygame.display.flip()


class Menu(pygame.sprite.Sprite):
    def __init__(self, group, img):
        super().__init__(group)
        self.image = pygame.image.load(img).convert_alpha()
        self.rect = self.image.get_rect()

    def pressed_the_button(self, event):
        x, y = event.pos
        if 213 <= x <= 687 and 421 <= y <= 480:
            return True
        return False


menu = pygame.sprite.Group()
Menu(menu, 'data/img/menu.png')
menu_run = True
while menu_run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            menu_run = False
            exit(0)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if menu.sprites()[0].pressed_the_button(event):
                menu_run = False
    menu.draw(screen)
    pygame.display.flip()


class Player(pygame.sprite.Sprite):
    def __init__(self, group, x, y, reaction_btn, img):
        super().__init__(group)
        self.name_img = img
        self.respawn_pos = (x, y)
        self.reaction_btn = reaction_btn
        self.course = {'first.png': 2, 'second.png': 0}[img]
        self.image = pygame.transform.rotate(pygame.image.load('data/img/' + img).convert_alpha(),
                                             90 * self.course)
        self.time_of_last_shooting, self.alive, self.time_of_last_death = True, True, 0
        self.rect = self.image.get_rect()
        self.can_die = True
        self.time_of_last_buff = 0
        self.rect.x = x
        self.rect.y = y

    def move_player(self, keys_press):
        btns = list(self.reaction_btn.keys())
        for btn in btns:
            if keys_press[btn] == 1:
                self.image = pygame.transform.rotate(self.image,
                                                     90 * (self.reaction_btn[btn][1] - self.course))
                self.course = self.reaction_btn[btn][1]
                nx, ny = self.reaction_btn[btn][0]
                for i in obstacles:
                    x_future, y_future = nx + self.rect.x, ny + self.rect.y
                    if i.rect.collidepoint(x_future, y_future) or \
                       i.rect.collidepoint(x_future + 44, y_future + 44) or \
                       i.rect.collidepoint(x_future + 44, y_future) or \
                       i.rect.collidepoint(x_future, y_future + 44):
                        return True
                if 855 >= self.rect.x + nx >= 0 and 855 >= self.rect.y + ny >= 0 and self.alive:
                    self.rect = self.rect.move(nx, ny)
                return True

    def fire(self, speed):
        shoot_period = 600
        if pygame.time.get_ticks() - self.time_of_last_shooting >= shoot_period and self.alive:
            courses_bullet = {0: (0, -speed), -1: (speed, 0), 2: (0, speed), 1: (-speed, 0)}
            sound = pygame.mixer.Sound('data/sound/shoot.wav')
            sound.set_volume(0.1)
            sound.play()
            Bullet(bullets, self.rect.x, self.rect.y, courses_bullet[self.course], self)
            self.time_of_last_shooting = pygame.time.get_ticks()

    def death(self):
        if self.alive and self.can_die:
            self.alive = False
            sound = pygame.mixer.Sound('data/sound/hit.wav')
            sound.set_volume(0.1)
            sound.play()
            self.time_of_last_death = pygame.time.get_ticks()
            self.respawn('data/img/' + self.name_img)

    def respawn(self, file):
        self.image = pygame.transform.rotate(pygame.image.load(file).convert_alpha(),
                                             90 * self.course)

        time_from_death = pygame.time.get_ticks() - self.time_of_last_death
        if time_from_death >= RESPAWN_PERIOD:
            self.alive = True
            self.rect.x, self.rect.y = self.respawn_pos
            self.image = pygame.transform.rotate(pygame.image.load(file).convert_alpha(),
                                                 90 * self.course)
            return
        # set frame
        frame_num = time_from_death // (RESPAWN_PERIOD // 7)
        if frame_num == 0:
            frame_num = 1
        name_boom_file = 'data/img/bang/kill' + str(frame_num) + '.png'
        self.image = pygame.transform.rotate(pygame.image.load(name_boom_file).convert_alpha(),
                                             90 * self.course)

    def update(self):
        if not self.can_die:
            if pygame.time.get_ticks() - self.time_of_last_buff >= TIME_OF_BUFF_ACTIVITY:
                self.can_die = True
        if self.can_die and self.name_img not in ['first.png', 'second.png']:
            if self is first_player:
                self.name_img = 'first.png'
            else:
                self.name_img = 'second.png'
            self.image = pygame.transform.rotate(
                pygame.image.load('data/img/' + self.name_img).convert_alpha(),
                90 * self.course)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, group, x, y, speed, parent):
        super().__init__(group)
        offset = 20
        self.parent = parent
        self.nx, self.ny = speed
        self.image = pygame.image.load('data/img/bullet.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x + offset
        self.rect.y = y + offset
        self.mask = pygame.mask.from_surface(self.image)

    def growth(self):
        self.rect = self.rect.move(self.nx, self.ny)
        if 900 < self.rect.x < 0 and 900 < self.rect.y < 0:
            self.kill()
            return True

        tank = pygame.sprite.spritecollideany(self, players)
        if tank is not None and tank != self.parent:
            self.kill()
            tank.death()
            return True

        bullet = pygame.sprite.spritecollideany(self, bullets)
        if bullet is not None and bullet != self:
            self.kill()
            bullet.kill()
            return True

        obstacle = pygame.sprite.spritecollideany(self, obstacles)
        if obstacle is not None and obstacle != self:
            self.kill()
            if not obstacle.strength:
                obstacle.kill()
            return True

        flag = pygame.sprite.spritecollideany(self, flags)
        if flag:
            global text_end
            text_end = flag.stop_game()
            self.kill()
            return True


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, group, pos, img, strength):
        super().__init__(group)
        self.image = pygame.image.load(img).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.strength = strength


class Flag(pygame.sprite.Sprite):
    def __init__(self, group, pos, img, text):
        super().__init__(group)
        self.image = pygame.image.load(img).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.text = text

    def stop_game(self):
        global run
        run = False
        return self.text


class Buff(pygame.sprite.Sprite):
    def __init__(self, group, pos, img):
        super().__init__(group)
        self.image = pygame.image.load(img).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        if pygame.sprite.collide_mask(self, first_player):
            first_player.can_die = False
            first_player.time_of_last_buff = pygame.time.get_ticks()
            first_player.name_img = 'first_with_buff.png'
            first_player.image = pygame.transform.rotate(pygame.image.load('data/img/' + first_player.name_img).convert_alpha(),
                                    90 * first_player.course)
            self.kill()
        if pygame.sprite.collide_mask(self, second_player):
            second_player.can_die = False
            second_player.time_of_last_buff = pygame.time.get_ticks()
            second_player.name_img = 'second_with_buff.png'
            second_player.image = pygame.transform.rotate(pygame.image.load('data/img/' + second_player.name_img).convert_alpha(),
                                    90 * second_player.course)
            self.kill()


def map_generator(xn, yn, size):
    with open('data/map/map.txt', 'r') as f:
        global map_list
        map_list = [a.split() for a in f.read().split('\n')]
    for y in range(yn):
        for x in range(xn):
            if map_list[y][x] == '1':
                Obstacle(obstacles, (x * size, y * size), 'data/img/bricks.png', False)
            elif map_list[y][x] == '2':
                Obstacle(obstacles, (x * size, y * size), 'data/img/irons.png', True)
            elif map_list[y][x][0] == '3':
                q = map_list[y][x][-1]
                a = {'1': ('data/img/flag_red.png', 'FIRST PLAYER'),
                     '2': ('data/img/flag_blue.png', 'SECOND PLAYER')}
                Flag(flags, (x * size, y * size), a[q][0], a[q][1])


first_player = Player(players, 0, 0, {119: ((0, -SPEED), 0),
                                      97: ((-SPEED, 0), 1),
                                      115: ((0, SPEED), 2),
                                      100: ((SPEED, 0), -1)}, 'first.png')
second_player = Player(players, 855, 855, {273: ((0, -SPEED), 0),
                                           276: ((-SPEED, 0), 1),
                                           274: ((0, SPEED), 2),
                                           275: ((SPEED, 0), -1)}, 'second.png')


def buff_generator():
    if len(buffs.sprites()) < MAX_BUFFS:
        while True:
            j, i = randint(0, 19), randint(0, 19)
            if map_list[i][j] == '0':
                break
        x, y = j * 45, i * 45
        Buff(buffs, (x, y), 'data/img/buff.png')


map_generator(20, 20, 45)
while run:
    pygame.time.Clock().tick(50)
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            exit(0)
        if event.type == BUFF_ID:
            buff_generator()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                first_player.fire(6)
            if event.key == pygame.K_RSHIFT:
                second_player.fire(6)

    keys = pygame.key.get_pressed()
    for i in players:
        i.move_player(keys)
    for i in bullets:
        i.growth()
    for i in players:
        if not i.alive:
            i.respawn('data/img/' + i.name_img)

    bullets.draw(screen)
    flags.draw(screen)
    obstacles.draw(screen)
    players.draw(screen)
    buffs.draw(screen)
    buffs.update()
    players.update()
    pygame.display.flip()

x = -900
y = 200
if len(text_end) == 13:
    y = 150
img = pygame.image.load('data/img/game_over.png').convert_alpha()
text_end = pygame.font.Font(None, 100).render(text_end, True, (255, 0, 0))
run = True

can_restart = False

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # TODO: make a restart
            print('restart')
            can_restart = False
            pass
    if x != 0:
        x += 1
        screen.blit(img, [x, 0])
        if x == 0:
            can_restart = True
            screen.blit(text_end, [y, 700])
        pygame.display.flip()

pygame.quit()
