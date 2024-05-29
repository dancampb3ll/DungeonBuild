import pygame
import random

class Slime(pygame.sprite.Sprite):
    def __init__(self, pygame_group, x, y):
        super().__init__(pygame_group)
        self.type = "npc"
        self.npc = "slime"
        self.health = 5
        self.ignorecolour = (255, 0, 255)
        self.image_visible = pygame.image.load(f"assets/npc/underworld/slime.png").convert_alpha()
        self.image_visible.set_colorkey(self.ignorecolour)
        self.image_invisible = pygame.Surface(self.image_visible.get_size(), pygame.SRCALPHA)
        self.image_invisible.fill((255, 0, 255))  # Fill with transparent color
        self.image_invisible.set_colorkey(self.ignorecolour)
        self.image = self.image_visible
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.damage_sfx = ["take_damage1.mp3"]
        self.death_sfx = ["death1.mp3"]

        self.ATTACK_INVINCIBILITY_TIME_LIMIT = 13
        self.invincibility_timecount = 0
        self.invincibility_timer_active = False
        self.image_showing = True


    def take_damage(self, weapon_damage):
        if not self.invincibility_timer_active:
            self.play_random_sfx_from_list(self.damage_sfx)
            self.invincibility_timer_active = True
            self.invincibility_timecount = 0
            self.health -= weapon_damage

        if self.health <= 0:
            self.play_random_sfx_from_list(self.death_sfx)
            self.die()

    def die(self):
        self.kill()

    def image_flash_refresh(self):
        FLASH_MODULUS = 4
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

    def update(self):
        self.manage_invincibility_state()
        self.image_flash_refresh()