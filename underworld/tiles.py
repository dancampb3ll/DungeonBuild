import settings
import pygame
import random


WALKABLE = ["cobblestone"]
underworldmapdict = {}
DEFAULT_NO_TILE_PORTAL = [None, None, None]
DARKNESS_PARAMETER = 0.6 #1 Max / #0.8 Recommended

DARKNESS_DEBUG = False
darkenmax = (255, 255, 255)

class UnderworldTile(pygame.sprite.Sprite):
    """A tile is initialised with a gridx and gridy location. The true x and true y are then multiples of these by the tile size.\n
    #Portal information to be given as [portaltype, (x, y), collisionSide]
    """
    def __init__(self, gridx, gridy, tiletypename, pygame_group, portal_information: list, player_mid_coords):
        
        super().__init__(pygame_group)
        self.type = "tile"
        self.tile = tiletypename
        self.ignorecolour = (255, 0, 255) #The pink colour on image backgrounds to be transparent
        self.raw_image = pygame.image.load(f"assets/underworldtiles/{self.tile}.png").convert_alpha()
        self.image = self.raw_image.copy() #Required in case of image modifications (such as highlight for build)
        self.image.set_colorkey(self.ignorecolour)
        self.rect = self.image.get_rect()
        self.gridx = gridx
        self.gridy = gridy
        self.rect.x = gridx * settings.UNDERWORLD_TILE_SIZE
        self.rect.y = gridy * settings.UNDERWORLD_TILE_SIZE
        self.portal_type = portal_information[0]
        self.portal_destination = None
        self.portal_collision_side = None
        self.apply_lighting_from_player(player_mid_coords)

    def apply_lighting_from_player(self, player_mid_coords):
        player_gridx = player_mid_coords[0] // settings.UNDERWORLD_TILE_SIZE
        player_gridy = player_mid_coords[1] // settings.UNDERWORLD_TILE_SIZE
        distance = ((self.gridx - player_gridx) ** 2 + (self.gridy - player_gridy) ** 2) ** 0.5
        
        
        #These two statements are to speed up the algorithm
        if distance > 14.7:
            return
        if distance > 8.1:
            self.image = self.raw_image.copy()
            self.image.fill(darkenmax, special_flags=pygame.BLEND_RGB_SUB)
        
        darken1 = (50*DARKNESS_PARAMETER, 60*DARKNESS_PARAMETER, 60*DARKNESS_PARAMETER)
        darken2 = (70*DARKNESS_PARAMETER, 80*DARKNESS_PARAMETER, 80*DARKNESS_PARAMETER) 
        darken3 = (90*DARKNESS_PARAMETER, 100*DARKNESS_PARAMETER, 100*DARKNESS_PARAMETER)
        darken4 = (110*DARKNESS_PARAMETER, 120*DARKNESS_PARAMETER, 120*DARKNESS_PARAMETER)
        darken5 = (130*DARKNESS_PARAMETER, 140*DARKNESS_PARAMETER, 140*DARKNESS_PARAMETER)
        darken6 = (150*DARKNESS_PARAMETER, 160*DARKNESS_PARAMETER, 160*DARKNESS_PARAMETER)
        darken7 = (170*DARKNESS_PARAMETER, 180*DARKNESS_PARAMETER, 180*DARKNESS_PARAMETER)
        darken8 = (190*DARKNESS_PARAMETER, 200*DARKNESS_PARAMETER, 200*DARKNESS_PARAMETER)
        darken9 = (210*DARKNESS_PARAMETER, 220*DARKNESS_PARAMETER, 220*DARKNESS_PARAMETER)
        if distance <= 1:
            self.image = self.raw_image.copy()
            self.image.fill(darken1, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 1.41 + 0.05:
            self.image = self.raw_image.copy()
            self.image.fill(darken2, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 2.24 + 0.05:
            self.image = self.raw_image.copy()
            self.image.fill(darken3, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 3.16 + 0.05:
            self.image = self.raw_image.copy()
            self.image.fill(darken4, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 4.12 + 0.05:
            self.image = self.raw_image.copy()
            self.image.fill(darken5, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 5.1 + 0.05:
            self.image = self.raw_image.copy()
            self.image.fill(darken6, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 6.08 + 0.05:
            self.image = self.raw_image.copy()
            self.image.fill(darken7, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 7.07 + 0.05:
            self.image = self.raw_image.copy()
            self.image.fill(darken8, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 8.06 + 0.05:
            self.image = self.raw_image.copy()
            self.image.fill(darken9, special_flags=pygame.BLEND_RGB_SUB)



def generate_new_map_dict_and_spawns():
    def generate_cobblestone_square_with_border(map, gridwidth, gridheight, start_x, start_y, spawn_stairs = False):
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
    
    def generate_cobblestone_walkway(map, gridwidth, gridheight, start_x, start_y):
        new_map = map
        for i in range(start_x, start_x + gridwidth):
            for j in range(start_y, start_y + gridheight):
                if new_map.get((i, j), None) == None or new_map.get((i, j), None)[0] == "border":
                    new_map[(i, j)] = ["cobblestone", DEFAULT_NO_TILE_PORTAL]
        #Adding border
        for i in range(start_x - 1, start_x + gridwidth + 1):
            for j in range(start_y - 1, start_y + gridheight + 1):
                if new_map.get((i, j), None) == None:
                    new_map[(i, j)] = ["border", DEFAULT_NO_TILE_PORTAL]
        return new_map 

    map = {}
    taken_ranges = []
    MIN_ROOMS = 4
    MAX_ROOMS = 12
    rooms = random.randint(MIN_ROOMS, MAX_ROOMS)
    rooms = 1
    
    #Spawn room:
    map = generate_cobblestone_square_with_border(map, 8, 16, 0, 0, True)
    
    map = generate_cobblestone_square_with_border(map, 8, 8, 4, 24)
    map = generate_cobblestone_walkway(map, 2, 11, 5, 15)

    return map, None