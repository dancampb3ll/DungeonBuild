import pygame

class Slime(pygame.sprite.Sprite):
    def __init__(self, pygame_group, x, y):
        super().__init__(pygame_group)
        self.type = "npc"
        self.npc = "slime"
        self.ignorecolour = (255, 0, 255)
        self.image = pygame.image.load(f"assets/npc/underworld/slime.png").convert()
        self.image.set_colorkey(self.ignorecolour)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
