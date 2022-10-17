# Importing Modules
import pygame
import os
import random

from pygame.font import Font

pygame.font.init()

# Window
width, height = 750, 750
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Invaders")

# Enemy Ship Images
red_space_ship = pygame.image.load(os.path.join("assets", "red_ship.png"))
green_space_ship = pygame.image.load(os.path.join("assets", "green_ship.png"))
blue_space_ship = pygame.image.load(os.path.join("assets", "blue_ship.png"))

# PLayer Ship Image
yellow_space_ship = pygame.image.load(os.path.join("assets", "space_ship.png"))

# Laser Images
red_laser = pygame.image.load(os.path.join("assets", "red_laser.png"))
green_laser = pygame.image.load(os.path.join("assets", "green_laser.png"))
blue_laser = pygame.image.load(os.path.join("assets", "blue_laser.png"))
purple_laser = pygame.image.load(os.path.join("assets", "purple_laser.png"))

# Background Image
bg = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (width, height))

# Button Image
start_img = pygame.image.load(os.path.join("assets", "start_button.png"))


class Button:
    def __init__(self, x, y, image, scale):
        self.width = image.get_width()
        self.height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def get_width(self):
        return self.width

    def draw(self, surface):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button on screen
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


class Laser:
    def __init__(self, x, y, img) -> object:
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x + 20, self.y - 30))

    def move(self, vel):
        self.y += vel

    def off_screen(self, laser_height):
        return not (laser_height >= self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOL_DOWN = 15

    def __init__(self, x, y, health=100):
        self.laser_img = None
        self.laser = None
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self):
        win.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(win)

    def move_lasers(self, vel, obj):
        self.cool_down()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cool_down(self):
        if self.cool_down_counter >= self.COOL_DOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def get_cool_down(self):
        return self.COOL_DOWN


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = yellow_space_ship
        self.laser_img = purple_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.score = 0

    def move_lasers(self, vel, objects) -> object:
        # global score
        self.cool_down()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objects:
                    if laser.collision(obj):
                        objects.remove(obj)
                        self.score += 1
                        if laser in self.lasers:
                            assert isinstance(laser, object)
                            self.lasers.remove(laser)

    def get_score(self):
        return self.score

    def draw(self, window) -> object:
        super().draw()
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, '#ff0000', (self.x, self.y + self.ship_img.get_height() + 10,
                                             self.ship_img.get_width(), 10))
        pygame.draw.rect(window, '#00ff00', (self.x, self.y + self.ship_img.get_height() + 10,
                                             self.ship_img.get_width() * (self.health / self.max_health), 10))


class Enemy(Ship):
    color_map = {
        "red": (red_space_ship, red_laser),
        "green": (green_space_ship, green_laser),
        "blue": (blue_space_ship, blue_laser)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.color_map[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x - 20, offset_y)) is not None


def redraw_window(player, main_font, lives, level, enemies, lost, lost_font):
    score = Player.get_score(player)
    win.blit(bg, (0, 0))
    # Draw Text
    lives_label = main_font.render(f"Lives: {lives}", 1, '#ffffff')
    level_label = main_font.render(f"Level: {level}", 1, '#ffffff')
    score_label = main_font.render(f"Score: {score}", 1, '#ffffff')

    win.blit(lives_label, (10, 10))
    win.blit(level_label, (width - level_label.get_width() - 10, 10))
    win.blit(score_label, (10, 60))

    for an_enemy in enemies:
        an_enemy.draw()

    player.draw(win)

    if lost:
        lost_label = lost_font.render("You Lost", 1, '#ffffff')
        win.blit(lost_label, (width / 2 - lost_label.get_width() / 2, 350))

    pygame.display.update()


def keyboard_inputs(player, player_vel):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] or keys[pygame.K_LEFT] and player.x - player_vel > 0:
        player.x -= player_vel
    if keys[pygame.K_d] or keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < width:
        player.x += player_vel
    if keys[pygame.K_w] or keys[pygame.K_UP] and player.y - player_vel > 0:
        player.y -= player_vel
    if keys[pygame.K_s] or keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < height:
        player.y += player_vel
    if keys[pygame.K_SPACE]:
        player.shoot()


def enemy_movement(enemies, enemy_vel, laser_vel, player, lives):
    for enemy in enemies:
        enemy.move(enemy_vel)
        enemy.move_lasers(-1 * laser_vel, player)

        if random.randrange(0, 240) == 1:
            enemy.shoot()

        if collide(enemy, player):
            player.health -= 5
            enemies.remove(enemy)

        elif enemy.y + enemy.get_height() > height:
            lives -= 1
            enemies.remove(enemy)


def main():
    run = True
    fps = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont('Comic Sans', 30)
    lost_font: Font = pygame.font.SysFont('Comic Sans', 40)

    enemies = []
    wave_length = 0
    enemy_vel = 1

    player_vel = 5
    laser_vel = -5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    while run:
        clock.tick(fps)

        redraw_window(player, main_font, lives, level, enemies, lost, lost_font)
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > fps * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, width - 100), random.randrange(-1500, -100),
                              random.choice(['red', 'blue', 'green']))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keyboard_inputs(player, player_vel)

        enemy_movement(enemies, enemy_vel, laser_vel, player, lives)

        player.move_lasers(laser_vel, enemies)


def main_menu():
    run = True

    start_button = Button(width/2 - 185, 250, start_img, 0.5)

    while run:
        win.blit(bg, (0, 0))
        start_button.draw(win)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if start_button.draw(win):
                main()

    pygame.quit()


main_menu()
