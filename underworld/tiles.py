import settings
import pygame
import random
import time

WALKABLE = ["cobblestone"]
underworldmapdict = {}
DEFAULT_NO_TILE_PORTAL = [None, None, None]
DARKNESS_PARAMETER = 0.6 #1 Max / #0.8 Recommended

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
        if not settings.DARKNESS_DEBUG: self.apply_lighting_from_player(player_mid_coords)

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
    def calculate_edge_tile_coords_from_room_created(room_width, room_height, topleftx, toplefty):
        left, right, top, bottom = [], [], [], []
        for x in range(0, room_height):
            top.append((topleftx + x, toplefty))
            bottom.append((topleftx + x, toplefty + room_height))
        for y in range(0, room_width):
            left.append((topleftx, toplefty + y))
            right.append((topleftx + room_width, toplefty + y))
        return left, right, top, bottom
    
    def generate_cobblestone_square_with_border(input_map, gridwidth, gridheight, start_x, start_y, spawn_stairs = False):
        new_map = input_map
        for i in range(start_x - 1, start_x + gridwidth + 1): #Adding border around spawn room
            for j in range(start_y - 1, start_y + gridheight + 1):
                new_map[(i, j)] = ["border", DEFAULT_NO_TILE_PORTAL]
        for i in range(start_x, start_x + gridwidth):
            for j in range(start_y, start_y + gridheight):
                new_map[(i, j)] = ["cobblestone", DEFAULT_NO_TILE_PORTAL]
        if spawn_stairs:
            new_map[(start_x + gridwidth - 1, start_y)] = ["stairs", ["overworld", (16, 16), "right"]]
        return new_map
    
    def generate_cobblestone_walkway(input_map, gridwidth, gridheight, start_x, start_y):
        new_map = input_map
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

    def generate_random_rooms_and_walkways(map):
        MIN_ROOMS = 4
        MAX_ROOMS = 12

        MIN_ROOMHEIGHT = 6
        MAX_ROOMHEIGHT = 14
        MIN_ROOMWIDTH = 4
        MAX_ROOMWIDTH = 14

        MIN_WALKWAY_DISTANCE = 3
        MAX_WALKWAY_DISTANCE = 14
        MIN_WALKWAY_THICKNESS = 2
        MAX_WALKWAY_THICKNESS = 2

        new_map = map
        roomcount = random.randint(MIN_ROOMS, MAX_ROOMS)
        roomcount = 5
        directions = ["left", "right", "top", "bottom"]

        previous_room_width = SPAWN_WIDTH
        previous_room_height = SPAWN_HEIGHT
        previous_room_x = SPAWN_X_TOPLEFT
        previous_room_y = SPAWN_Y_TOPLEFT
        for i in range(roomcount):
            collide_checks_passed = False
            while collide_checks_passed == False:
                collide_check_map = {}
                left_wall, right_wall, top_wall, bottom_wall = calculate_edge_tile_coords_from_room_created(previous_room_width, previous_room_height, previous_room_x, previous_room_y)
                wall_side = directions[random.randint(0, len(directions)-1)]
                if wall_side == "left":
                    wall = left_wall
                elif wall_side == "right":
                    wall = right_wall
                elif wall_side == "top":
                    wall = top_wall
                elif wall_side == "bottom":
                    wall = bottom_wall

                wall_coord_selection = wall[random.randint(0, len(left_wall)-1)]

                walkway_distance = random.randint(MIN_WALKWAY_DISTANCE, MAX_WALKWAY_DISTANCE)
                walkway_thickness = random.randint(MIN_WALKWAY_THICKNESS, MAX_WALKWAY_THICKNESS)
                new_room_width = random.randint(MIN_ROOMWIDTH, MAX_ROOMWIDTH)
                new_room_height = random.randint(MIN_ROOMHEIGHT, MAX_ROOMHEIGHT)

                if wall_side == "left" or wall_side == "right":
                    walkway_width = walkway_distance
                    walkway_height = walkway_thickness
                else:
                    walkway_width = walkway_thickness
                    walkway_height = walkway_distance
                if wall_side == "left":
                    new_room_x_start = wall_coord_selection[0] - walkway_distance - new_room_width
                    new_room_y_start = wall_coord_selection[1]
                    walkway_startx = wall_coord_selection[0] - walkway_distance
                    walkway_starty = wall_coord_selection[1]
                elif wall_side == "right":
                    new_room_x_start = wall_coord_selection[0] + walkway_distance
                    new_room_y_start = wall_coord_selection[1]
                    walkway_startx = wall_coord_selection[0]
                    walkway_starty = wall_coord_selection[1]
                elif wall_side == "top":
                    new_room_x_start = wall_coord_selection[0]
                    new_room_y_start = wall_coord_selection[1] - walkway_distance - new_room_height
                    walkway_startx = wall_coord_selection[0]
                    walkway_starty = wall_coord_selection[1] - walkway_distance
                elif wall_side == "bottom":
                    new_room_x_start = wall_coord_selection[0]
                    new_room_y_start = wall_coord_selection[1] + walkway_distance
                    walkway_startx = wall_coord_selection[0]
                    walkway_starty = wall_coord_selection[1]

                collide_check_map = generate_cobblestone_square_with_border({}, new_room_width, new_room_height, new_room_x_start, new_room_y_start)

                collide_check_map = generate_cobblestone_walkway(collide_check_map, walkway_width, walkway_height, walkway_startx, walkway_starty)
                collide_checks_passed = True
                for coord in collide_check_map.keys():
                    if collide_check_map[coord][0] == "border":
                        break
                    material_check = new_map.get(coord, ["border"])[0]
                    if material_check != "border":
                        collide_checks_passed = False
                        print("Collision at ", coord, " : ", "old material: ", material_check, "new material: ", collide_check_map[coord])
                        break
                    print("No collision")
            
            for coord in collide_check_map.keys():
                if new_map.get(coord, None) is None:
                    new_map[coord] = collide_check_map[coord]
                elif new_map.get(coord, None)[0] == "border":
                    new_map[coord] = collide_check_map[coord]

            previous_room_x = new_room_x_start
            previous_room_y = new_room_y_start
            previous_room_width = new_room_width
            previous_room_height = new_room_height

            print(len(new_map.keys()))
        return new_map

    map = {}
    taken_ranges = []

    
    #Spawn room:
    SPAWN_WIDTH, SPAWN_HEIGHT, SPAWN_X_TOPLEFT, SPAWN_Y_TOPLEFT = 8, 16, 0, 0
    map = generate_cobblestone_square_with_border(map, SPAWN_WIDTH, SPAWN_HEIGHT, SPAWN_X_TOPLEFT, SPAWN_Y_TOPLEFT, True)

    #map = generate_cobblestone_square_with_border(map, 8, 8, 4, 24)
    map = generate_random_rooms_and_walkways(map)

    return map, None