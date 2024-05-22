import settings
import pygame

underworldmapdict = {}


class UnderworldTile(pygame.sprite.Sprite):
    """A tile is initialised with a gridx and gridy location. The true x and true y are then multiples of these by the tile size.\n
    #Portal information to be given as [portaltype, (x, y), collisionSide]
    """
    def __init__(self, gridx, gridy, tiletypename, pygame_group, portal_information: list):
        
        super().__init__(pygame_group)
        self.type = "tile"
        self.tile = tiletypename
        self.ignorecolour = (255, 128, 255) #The pink colour on image backgrounds to be transparent
        self.image = pygame.image.load(f"assets/underworldtiles/{self.tile}.png").convert()
        self.raw_image = self.image.copy() #Required in case of image modifications (such as highlight for build)
        self.image.set_colorkey(self.ignorecolour)
        self.rect = self.image.get_rect()
        self.gridx = gridx
        self.gridy = gridy
        self.rect.x = gridx * settings.UNDERWORLD_TILE_SIZE
        self.rect.y = gridy * settings.UNDERWORLD_TILE_SIZE
        self.portal_type = portal_information[0]
        self.portal_destination = None
        self.portal_collision_side = None