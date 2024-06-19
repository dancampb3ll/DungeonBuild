import settings
import pygame
import random
import time

WALKABLE = ["cobblestone", "cobblestoneMossy", "woodenPlank"]
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

SPAWN_WIDTH, SPAWN_HEIGHT, SPAWN_X_TOPLEFT, SPAWN_Y_TOPLEFT = 8, 16, 0, 0

def check_adjacent_and_diagonal_tiles_walkable(map, coord):
        x = coord[0]
        y = coord[1]
        adjacent_and_diagonal_coords = []
        for i in range(0, 3):
            for j in range(0, 3):
                checkx = x + i - 1
                checky = y + j - 1
                if (checkx, checky) != coord:
                    adjacent_and_diagonal_coords.append((checkx, checky))
        print(adjacent_and_diagonal_coords)
        for coordinate in adjacent_and_diagonal_coords:
            if map[coordinate][0] not in WALKABLE:
                return False
        return True

def calculate_edge_tile_coords_from_room_created(room_width, room_height, topleftx, toplefty):
    left, right, top, bottom = [], [], [], []
    for x in range(0, room_width):
        top.append((topleftx + x, toplefty))
        bottom.append((topleftx + x, toplefty + room_height))
    for y in range(0, room_height):
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

def generate_small_wooden_loot_island(map):
    WALKWAY_LENGTH = 6
    new_map = {}
    start_tile_potentials = list(map.keys())
    
    collision = True

    while collision:
        #Selecting tile randomly to generate structure in
        new_map = {}
        random_start_tile = start_tile_potentials[random.randint(0, len(start_tile_potentials) - 1)]
        topleftx = random_start_tile[0]
        toplefty = random_start_tile[1]
        
        #Making path
        for i in range(0, WALKWAY_LENGTH):
            new_map[(topleftx - 1, toplefty + i)] = ["woodenPlank", DEFAULT_NO_TILE_PORTAL]
            new_map[(topleftx, toplefty + i)] = ["woodenPlank", DEFAULT_NO_TILE_PORTAL]
        
        #Making cross section
        for i in range(0,8):
            for j in range(0, 11):
                new_map[(topleftx - 3 + i, toplefty + WALKWAY_LENGTH + j)] = ["woodenPlank", DEFAULT_NO_TILE_PORTAL]
        new_map[(topleftx - 3 + 7, toplefty + WALKWAY_LENGTH + 10)] = ["rope", ["overworld", (16, 16), "right"]]


        #Collision checks
        collision_list = []
        for coord in new_map.keys():
            if map.get((coord), ["border"])[0] != "border":
                collision_list.append(coord)
        if len(collision_list) == 0:
            collision = False

        
    #Making border:
    new_map_xs = []
    new_map_ys = []
    for coord in new_map.keys():
        new_map_xs.append(coord[0])
        new_map_ys.append(coord[1])

    min_x = min(new_map_xs)
    min_y = min(new_map_ys)
    max_x = max(new_map_xs)
    max_y = max(new_map_ys)
    for i in range(min_x - 1, max_x + 2):
        for y in range(min_y - 1, max_y + 2):
            if new_map.get((i, y), None) == None:
                new_map[(i, y)] = ["border", DEFAULT_NO_TILE_PORTAL]

    for coord in new_map.keys():
        if map.get(coord, ["border"])[0] == "border":
            map[coord] = new_map[coord]

    return map

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

def add_boulderSmall_randomly(map):
    BOULDERSMALL_CHANCE = 140
    for coord in map.keys():
        if map[coord][0] == "cobblestone":
            if random.randint(0, BOULDERSMALL_CHANCE) == BOULDERSMALL_CHANCE:
                if check_adjacent_and_diagonal_tiles_walkable(map, coord) == True:
                    map[coord][0] = "boulderSmall"
    return map

def generate_new_map_dict_and_spawns():
    def add_mossy_cobblestone_randomly(map):
        MOSSY_CHANCE = 15
        for coord in map.keys():
            if map[coord][0] == "cobblestone":
                if random.randint(0, MOSSY_CHANCE) == MOSSY_CHANCE:
                    map[coord][0] = "cobblestoneMossy"
        return map
 
    def generate_slime_spawns(map):
        SLIME_SPAWN_CHANCE = 90
        spawns = {}
        for coord in map.keys():
            if map[coord][0] in WALKABLE:
                if random.randint(0, SLIME_SPAWN_CHANCE) == SLIME_SPAWN_CHANCE:
                    spawns[coord] = "slime"
        return spawns

    def generate_skeleton_spawns(map):
        SKELTON_SPAWN_CHANCE = 400
        spawns = {}
        for coord in map.keys():
            if map[coord][0] in WALKABLE:
                if random.randint(0, SKELTON_SPAWN_CHANCE) == SKELTON_SPAWN_CHANCE:
                    spawns[coord] = "skeleton"
        return spawns

    map = {}
    
    #Spawn room:
    spawn_width, spawn_height, spawn_x_topleft, spawn_y_topleft = SPAWN_WIDTH, SPAWN_HEIGHT, SPAWN_X_TOPLEFT, SPAWN_Y_TOPLEFT
    map = generate_cobblestone_square_with_border(map, spawn_width, spawn_height, spawn_x_topleft, spawn_y_topleft, True)

    map = generate_random_rooms_and_walkways(map)

    map = add_boulderSmall_randomly(map)

    map = add_mossy_cobblestone_randomly(map)

    map = generate_small_wooden_loot_island(map)

    spawns = {}
    slime_spawns = generate_slime_spawns(map)
    skeleton_spawns = generate_skeleton_spawns(map)

    for coord in slime_spawns.keys():
        spawns[coord] = slime_spawns[coord]
    for coord in skeleton_spawns.keys():
        spawns[coord] = skeleton_spawns[coord]

    return map, spawns

def generate_random_rooms_and_walkways(map):
    MIN_ROOMS = 4
    MAX_ROOMS = 12

    MIN_ROOMHEIGHT = 4
    MAX_ROOMHEIGHT = 15
    MIN_ROOMWIDTH = 3
    MAX_ROOMWIDTH = 17

    MIN_WALKWAY_DISTANCE = 3
    MAX_WALKWAY_DISTANCE = 18
    MIN_WALKWAY_THICKNESS = 2
    MAX_WALKWAY_THICKNESS = 3

    new_map = map
    roomcount = random.randint(MIN_ROOMS, MAX_ROOMS)
    directions = ["left", "right", "top", "bottom"]

    previous_room_width = SPAWN_WIDTH
    previous_room_height = SPAWN_HEIGHT
    previous_room_x = SPAWN_X_TOPLEFT
    previous_room_y = SPAWN_Y_TOPLEFT
    for i in range(roomcount):
        left_wall, right_wall, top_wall, bottom_wall = calculate_edge_tile_coords_from_room_created(previous_room_width, previous_room_height, previous_room_x, previous_room_y)
        wall_side = directions[random.randint(0, len(directions)-1)]
        if i == 0: wall_side = "bottom"
        if wall_side == "left":
            wall = left_wall
        elif wall_side == "right":
            wall = right_wall
        elif wall_side == "top":
            wall = top_wall
        elif wall_side == "bottom":
            wall = bottom_wall

        wall_coord_selection = wall[random.randint(0, len(wall)-1)]

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

        #print(f"Wall coords: {wall}")
        #print(f"ROOM {i + 1}: Building from {wall_side} wall, coordinate ({wall_coord_selection[0]}, {wall_coord_selection[1]})")

        new_room = generate_cobblestone_square_with_border({}, new_room_width, new_room_height, new_room_x_start, new_room_y_start)
        new_walkway = generate_cobblestone_walkway({}, walkway_width, walkway_height, walkway_startx, walkway_starty)
        
        #For rooms, replace empty spaces only.
        newcobblestone_oldborder_list = []
        for coord in new_room.keys():
            if new_map.get(coord, None) == None:
                new_map[coord] = new_room[coord]
            elif new_map.get(coord, ["border"])[0] == "border" and new_room[coord][0] == "cobblestone":
                newcobblestone_oldborder_list.append(coord)
        #Get a list of the existing map border intersections with the new room cobblestone, and then create one hole.
        for i in range(0, 2):
            if newcobblestone_oldborder_list != []:
                random_hole = newcobblestone_oldborder_list.pop(random.randint(0, len(newcobblestone_oldborder_list)-1))
                new_map[random_hole] = new_room[random_hole]

        #For walkways, replace empty spaces AND borders
        for coord in new_walkway.keys():
            if new_map.get(coord, ["border"])[0] == "border":
                new_map[coord] = new_walkway[coord]

        previous_room_x = new_room_x_start
        previous_room_y = new_room_y_start
        previous_room_width = new_room_width
        previous_room_height = new_room_height

    return new_map