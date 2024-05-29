import pygame
import random

class Slime(pygame.sprite.Sprite):
    def __init__(self, pygame_group, x, y):
        super().__init__(pygame_group)
        self.type = "npc"
        self.npc = "slime"
        self.health = 5
        self.ignorecolour = (255, 0, 255)
        self.image = pygame.image.load(f"assets/npc/underworld/slime.png").convert()
        self.image.set_colorkey(self.ignorecolour)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.damage_sfx = ["take_damage1.mp3"]
        self.death_sfx = ["death1.mp3"]

        self.ATTACK_INVINCIBILITY_TIME_LIMIT = 13
        self.invincibility_timecount = 0
        self.invincibility_timer_active = False

    def take_damage(self, weapon_damage):
        if self.invincibility_timecount >= self.ATTACK_INVINCIBILITY_TIME_LIMIT:
                self.invincibility_timer_active = False
                self.invincibility_timecount = 0
        
        if self.invincibility_timer_active:
            self.invincibility_timecount += 1
        else:
            self.play_random_sfx_from_list(self.damage_sfx)
            self.invincibility_timer_active = True
            self.invincibility_timecount = 0
            self.health -= weapon_damage
        
        if self.health <= 0:
            self.play_random_sfx_from_list(self.death_sfx)
            self.die()

    def die(self):
        self.kill()

    def play_random_sfx_from_list(self, sfx_list):
        sfx_list = sfx_list
        random_sfx_num = random.randint(0, len(sfx_list) - 1)
        sfx = pygame.mixer.Sound(f"assets/sfx/underworld/{self.npc}/{sfx_list[random_sfx_num]}")
        sfx.play()