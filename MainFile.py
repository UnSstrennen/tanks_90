import pygame


RESPAWN_PERIOD, SPEED = 1000, 5
run, move_tank = True, False
time_of_last_shooting, fires = 0, []
players = pygame.sprite.Group()
bullets = pygame.sprite.Group()


pygame.init()
screen = pygame.display.set_mode((900, 900))
screen.blit(pygame.image.load("img/background.png").convert(), [0, 0])


pygame.mixer.init()
background_sound = pygame.mixer.Sound('sound/background_music.wav')
background_sound.set_volume(0.5)
background_sound.play(-1)


shoot_clock = pygame.time.Clock()
clock = pygame.time.Clock()
clock.tick()
pygame.display.flip()


class Player(pygame.sprite.Sprite):
    def __init__(self, group, x, y, reaction_btn, img):
        super().__init__(group)
        self.name_img = img
        self.respawn_pos = (x, y)
        self.reaction_btn = reaction_btn
        self.course = {'first.png': 2, 'second.png': 0}[img]
        self.image = pygame.transform.rotate(pygame.image.load('img/' + img).convert_alpha(),
                                             90 * self.course)
        self.time_of_last_shooting, self.alive, self.time_of_last_death = True, True, 0
        self.rect = self.image.get_rect()
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
                if 855 >= self.rect.x + nx >= 0 and 855 >= self.rect.y + ny >= 0 and self.alive:
                    self.rect = self.rect.move(nx, ny)
                return True

    def fire(self, speed):
        shoot_period = 600
        if pygame.time.get_ticks() - self.time_of_last_shooting >= shoot_period and self.alive:
            courses_bullet = {0: (0, -speed), -1: (speed, 0), 2: (0, speed), 1: (-speed, 0)}
            sound = pygame.mixer.Sound('sound/shoot.wav')
            sound.set_volume(0.1)
            sound.play()
            Bullet(bullets, self.rect.x, self.rect.y, courses_bullet[self.course], self)
            self.time_of_last_shooting = pygame.time.get_ticks()

    def death(self):
        if self.alive:
            self.alive = False
            sound = pygame.mixer.Sound('sound/hit.wav')
            sound.set_volume(0.1)
            sound.play()
            self.time_of_last_death = pygame.time.get_ticks()
            self.respawn('img/' + self.name_img)

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
        name_boom_file = 'img/bang/kill' + str(frame_num) + '.png'
        self.image = pygame.transform.rotate(pygame.image.load(name_boom_file).convert_alpha(),
                                             90 * self.course)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, group, x, y, speed, parent):

        super().__init__(group)
        offset = 20
        self.parent = parent
        self.nx, self.ny = speed
        self.image = pygame.image.load('img/bullet.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x + offset
        self.rect.y = y + offset

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


first_player = Player(players, 0, 0, {119: ((0, -SPEED), 0),
                                      97: ((-SPEED, 0), 1),
                                      115: ((0, SPEED), 2),
                                      100: ((SPEED, 0), -1)}, 'first.png')
second_player = Player(players, 0, 500, {273: ((0, -SPEED), 0),
                                         276: ((-SPEED, 0), 1),
                                         274: ((0, SPEED), 2),
                                         275: ((SPEED, 0), -1)}, 'second.png')
while run:
    pygame.time.Clock().tick(60)
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                first_player.fire(6)
            if event.key == pygame.K_QUOTE:
                second_player.fire(6)

    keys = pygame.key.get_pressed()
    for i in players:
        i.move_player(keys)
    for i in bullets:
        i.growth()

    for i in players:
        if not i.alive:
            i.respawn('img/' + i.name_img)

    bullets.draw(screen)
    players.draw(screen)
    pygame.display.flip()
