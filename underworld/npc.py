import pygame

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
            self.invincibility_timer_active = True
            self.invincibility_timecount = 0
            self.health -= weapon_damage
            print(self.health)