import pygame
import random
import math
import settings

def calculate_distance_pythagoras(point1: tuple, point2: tuple):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

class Slime(pygame.sprite.Sprite):
    def __init__(self, pygame_group, x, y):
        super().__init__(pygame_group)
        self.type = "npc"
        self.npc = "slime"
        self.health = 5
        self.speed = 1
        self.ignorecolour = (255, 0, 255)
        self.image_visible = pygame.image.load(f"assets/npc/underworld/slime.png").convert_alpha()
        self.image_visible.set_colorkey(self.ignorecolour)
        self.image_invisible = pygame.Surface(self.image_visible.get_size(), pygame.SRCALPHA)
        self.image_invisible.fill((255, 0, 255))  # Fill with transparent color
        self.image_invisible.set_colorkey(self.ignorecolour)
        self.image = self.image_visible
        self.aggression_distance = 200

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.damage_sfx = ["take_damage1.mp3"]
        self.death_sfx = ["death1.mp3"]
        self.knockbackx = None
        self.knockbacky = None

        self.ATTACK_INVINCIBILITY_TIME_LIMIT = 13
        self.invincibility_timecount = 0
        self.invincibility_timer_active = False
        self.image_showing = True

    def take_damage(self, weapon):
        weapon_damage = weapon.damage

        if not self.invincibility_timer_active:
            self.play_random_sfx_from_list(self.damage_sfx)
            self.invincibility_timer_active = True
            self.invincibility_timecount = 0
            self.health -= weapon_damage
            self.set_knockback_position(weapon)

        if self.health <= 0:
            self.play_random_sfx_from_list(self.death_sfx)
            self.die()

    def set_knockback_position(self, weapon):
        weapon_direction = weapon.player_direction
        weapon_knockback = weapon.knockback
        if weapon_direction == "left":
            self.knockbackx = self.rect.x - weapon_knockback
        elif weapon_direction == "right":
            self.knockbackx = self.rect.x + weapon_knockback
        elif weapon_direction == "up":
            self.knockbacky = self.rect.y - weapon_knockback
        elif weapon_direction == "down":
            self.knockbackx = self.rect.x + weapon_knockback

    def perform_knockback(self):
        if self.knockbackx == None and self.knockbacky == None:
            return
        knockback_speed = settings.KNOCKBACK_SPEED

        if self.knockbackx != None:
            if self.knockbackx > self.rect.x:
                self.rect.x = min(self.knockbackx, self.rect.x + knockback_speed)
            elif self.knockbackx < self.rect.x:
                self.rect.x = max(self.knockbackx, self.rect.x - knockback_speed)
            else:
                self.knockbackx = None

        if self.knockbacky != None:
            if self.knockbacky > self.rect.y:
                self.rect.y = min(self.knockbacky, self.rect.y + knockback_speed)
            elif self.knockbacky < self.rect.y:
                self.rect.y = max(self.knockbacky, self.rect.y - knockback_speed)
            else:
                self.knockbacky = None




    def die(self):
        self.kill()

    def image_flash_refresh(self):
        FLASH_MODULUS = 6
        if self.invincibility_timer_active == False:
            self.image_showing = True
            self.image = self.image_visible
            return
        if self.invincibility_timecount % FLASH_MODULUS == 0:
            self.image_showing = not self.image_showing
            if self.image_showing == True:
                self.image = self.image_visible
            else:
                self.image = self.image_invisible

    def manage_invincibility_state(self):
        if self.invincibility_timer_active:
            self.invincibility_timecount += 1
            if self.invincibility_timecount >= self.ATTACK_INVINCIBILITY_TIME_LIMIT:
                self.invincibility_timer_active = False
                self.invincibility_timecount = 0

    def play_random_sfx_from_list(self, sfx_list):
        sfx_list = sfx_list
        random_sfx_num = random.randint(0, len(sfx_list) - 1)
        sfx = pygame.mixer.Sound(f"assets/sfx/underworld/{self.npc}/{sfx_list[random_sfx_num]}")
        sfx.play()

    def basic_pathfind(self, player):
        if self.knockbackx != None or self.knockbacky != None:
            return
        player_rect = player.rect
        player_center_pos = player_rect.center
        distance_from_player = calculate_distance_pythagoras(self.rect.center, player_center_pos)
        if self.rect.collidepoint(player_rect.center):
            self.attack_sequence(player)
            return
        if distance_from_player < self.aggression_distance:
            if self.rect.x < player_center_pos[0]:
                self.rect.x += self.speed
            elif self.rect.x > player_center_pos[0]:
                self.rect.x -= self.speed
            if self.rect.y < player_center_pos[1]:
                self.rect.y += self.speed
            elif self.rect.y > player_center_pos[1]:
                self.rect.y -= self.speed

    def attack_sequence(self, player):
        None

    def update(self):
        self.manage_invincibility_state()
        self.perform_knockback()
        self.image_flash_refresh()
        