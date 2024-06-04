import settings
import pygame
import random


WALKABLE = ["cobblestone"]
underworldmapdict = {}
DEFAULT_NO_TILE_PORTAL = [None, None, None]

class UnderworldTile(pygame.sprite.Sprite):
    """A tile is initialised with a gridx and gridy location. The true x and true y are then multiples of these by the tile size.\n
    #Portal information to be given as [portaltype, (x, y), collisionSide]
    """
    def __init__(self, gridx, gridy, tiletypename, pygame_group, portal_information: list):
        
        super().__init__(pygame_group)
        self.type = "tile"
        self.tile = tiletypename
        self.ignorecolour = (255, 0, 255) #The pink colour on image backgrounds to be transparent
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


def generate_new_map_dict_and_spawns():
    def generate_cobblestone_square_with_border(map, gridheight, gridwidth, start_x, start_y, spawn_stairs = False):
        new_map = map
        for i in range(start_x - 1, start_x + gridwidth + 1): #Adding border around spawn room
            for j in range(start_y - 1, start_y + gridheight + 1):
                new_map[(i, j)] = ["border", DEFAULT_NO_TILE_PORTAL]
        for i in range(start_x, start_x + gridwidth):
            for j in range(start_y, start_y + gridheight):
                new_map[(i, j)] = ["cobblestone", DEFAULT_NO_TILE_PORTAL]
        if spawn_stairs:
            new_map[(start_x + gridwidth - 1, start_y)] = ["stairs", ["overworld", (16, 16), "right"]]
        return new_map
        
    

    map = {}
    taken_ranges = []
    MIN_ROOMS = 4
    MAX_ROOMS = 12
    rooms = random.randint(MIN_ROOMS, MAX_ROOMS)
    rooms = 1
    
    #Spawn room:
    map = generate_cobblestone_square_with_border(map, 8, 8, 0, 0, True)

    return map, None