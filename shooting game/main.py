import pygame
from pygame import mixer
import os
import random
mixer.init()
pygame.font.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 600, 800

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space shooting")

#  Load music and sounds

pygame.mixer.music.load('/Users/AlanChauque/Desktop/shooting game/sounds/music.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0.0, 1000)
shoot_fx = pygame.mixer.Sound('/Users/AlanChauque/Desktop/shooting game/sounds/shoot.mp3')
pygame.mixer.music.set_volume(0.5)

# Load images
RED_SHIP = pygame.image.load(
    os.path.join("assets", "/Users/AlanChauque/Desktop/shooting game/assets/RED_ship.png"))
METEORITE = pygame.image.load(
    os.path.join("assets", "/Users/AlanChauque/Desktop/shooting game/assets/meteorite.png"))
BLUE_SHIP = pygame.image.load(
    os.path.join("assets", "/Users/AlanChauque/Desktop/shooting game/assets/BLUE_ship.png"))

# Player
MAIN_SHIP = pygame.image.load(
    os.path.join("assets", "/Users/AlanChauque/Desktop/shooting game/assets/main_ship.png"))

# Lasers
RED_BULLET = pygame.image.load(os.path.join("assets", "/Users/AlanChauque/Desktop/shooting game/assets/RED_bullet.png"))
METEORITE_PIECE = pygame.image.load(
    os.path.join("assets", "/Users/AlanChauque/Desktop/shooting game/assets/METEORITE_PIECE.png"))
BLUE_BULLET = pygame.image.load(os.path.join("assets", "/Users/AlanChauque/Desktop/shooting game/assets/BLUE_bullet.png"))
MAIN_ROCKET = pygame.image.load(
    os.path.join("assets", "/Users/AlanChauque/Desktop/shooting game/assets/main_rocket.png"))

# Background
BG = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "/Users/AlanChauque/Desktop/shooting game/assets/background.jpg")),
    (SCREEN_WIDTH, SCREEN_HEIGHT))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (height >= self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(SCREEN_HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            shoot_fx.play()

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = MAIN_SHIP
        self.laser_img = MAIN_ROCKET
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(SCREEN_HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (
            self.x, self.y + self.ship_img.get_height() + 10,
            self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.ship_img.get_height() + 10,
            self.ship_img.get_width() * (self.health / self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
        "RED": (RED_SHIP, RED_BULLET),
        "GREEN": (METEORITE, METEORITE_PIECE),
        "BLUE": (BLUE_SHIP, BLUE_BULLET)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
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
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("raleway", 50)
    lost_font = pygame.font.SysFont("raleway", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_velocity = 5
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        SCREEN.blit(BG, (0, 0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", True, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", True, (255, 255, 255))

        SCREEN.blit(lives_label, (10, 10))
        SCREEN.blit(level_label,
                    (SCREEN_WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(SCREEN)

        player.draw(SCREEN)

        if lost:
            lost_label = lost_font.render("You Lost!!!", True, (255, 255, 255))
            SCREEN.blit(lost_label, (SCREEN_WIDTH
                                     / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, SCREEN_WIDTH
                                               - 100),
                              random.randrange(-1500, -100),
                              random.choice(["RED", "BLUE", "GREEN"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_velocity > 0:  # left
            player.x -= player_velocity
        if keys[
            pygame.K_RIGHT] and player.x + player_velocity + player.get_width()\
                < SCREEN_WIDTH:  # right
            player.x += player_velocity
        if keys[pygame.K_UP] and player.y - player_velocity > 0:  # up
            player.y -= player_velocity
        if keys[
            pygame.K_DOWN] and player.y + player_velocity + player.get_height()\
                + 15 < SCREEN_HEIGHT:  # down
            player.y += player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > SCREEN_HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("raleway", 60)
    run = True
    while run:
        SCREEN.blit(BG, (0, 0))
        title_label = title_font.render("Press the mouse to begin...", True,
                                        (255, 255, 255))
        SCREEN.blit(title_label,
                    (SCREEN_WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
