import overworld.buildings
import pygame
import settings
import utils

"""
This tab defines tile mappings, their properties such as building buildable, 
"""

class OutdoorTile(pygame.sprite.Sprite):
    """A tile is initialised with a gridx and gridy location. The true x and true y are then multiples of these by the tile size.\n
    #Portal information to be given as [portaltype, (x, y), collisionSide]
    """
    def __init__(self, gridx, gridy, tiletypename, pygame_camera, portal_information: list):
        
        super().__init__(pygame_camera)
        self.type = "tile"
        self.tile = tiletypename
        self.ignorecolour = (255, 128, 255) #The pink colour on image backgrounds to be transparent
        if self.tile == "overgroundBorder":
            self.ignorecolour = (0, 0, 0)
        self.image = pygame.image.load(f"assets/overworldtiles/{self.tile}.png").convert()
        self.raw_image = self.image.copy() #Required in case of image modifications (such as highlight for build)
        self.image.set_colorkey(self.ignorecolour)
        self.rect = self.image.get_rect()
        self.gridx = gridx
        self.gridy = gridy
        self.rect.x = gridx * settings.OVERWORLD_TILE_SIZE
        self.rect.y = gridy * settings.OVERWORLD_TILE_SIZE
        self.portal_information = portal_information
        self.portal_type = portal_information[0]
        self.portal_destination = None
        self.portal_collision_side = None

    def __json__(self):
        json_data = {
            "gridx": self.gridx,
            "gridy": self.gridy,
            "tile": self.tile,
            "portal_information": self.portal_information
        }
        return json_data

    def update(self):
        None
        #self.image.set_colorkey(self.ignorecolour)


WALKABLE = ["overgroundGrass", "tinyFlower", "cobblestone"]
BUILDABLE = ["overgroundGrass"]
TILE_MAPPINGS = {
    0: None,
    1: "overgroundGrid",
    2: "overgroundGrass",
    3: "overgroundWater",
    4: "overgroundBorder",
    5: "overgroundSmallDungeonLeft",
    6: "overgroundSmallDungeonRight",
    7: "tinyPot",
    8: "fenceTopLeft",
    9: "fenceTop",
    10: "fenceTopRight",
    11: "fenceLeft",
    12: "fenceRight",
    13: "fenceBottomLeft",
    14: "fenceBottom",
    15: "fenceBottomRight",
    16: "tinyFlower",
    17: "cobblestone"
}

def detect_building_worldmap_collision_place_and_changes(worldmapdict, overworldbuilding, topleftTile: tuple, player_coords_list_to_avoid_building_on):
    """Takes the current world map dictionary, a building that is to be built, and the top left tile (that the player is clicking on).
    The building type looks up functions from the overworld.buildings page, and uses this to get the tile locations for a certain building type relative to the top left tile the player
    has clicked to build on.\n
    Also checks that the player is not standing on a position where a building is to be placed, and prevents this if so.
    Returns a tile dictionary, coordinate changes. A change is given in format [(x,y), changenum]
    """
    #dynamic method invocation
    building_functions = overworld.buildings.building_functions
    
    building_function = building_functions.get(overworldbuilding)

    if building_function is not None:
        building_coord_dict = building_function(topleftTile)
    else:
        raise ValueError("Unknown building type: {}".format(overworldbuilding))

    changes = []
    for coordinate in building_coord_dict.keys():
        tilenum = worldmapdict.get(coordinate)
        tilename = TILE_MAPPINGS[tilenum]
        if tilename == "overgroundBorder":
            utils.FloatingText(utils.floating_text_group, topleftTile[0] * settings.OVERWORLD_TILE_SIZE, topleftTile[1] * settings.OVERWORLD_TILE_SIZE,
                    "You must build grass here first.", colour=(255, 30, 50), font_size=12)
            return None
        if tilename not in BUILDABLE:
            utils.FloatingText(utils.floating_text_group, topleftTile[0] * settings.OVERWORLD_TILE_SIZE, topleftTile[1] * settings.OVERWORLD_TILE_SIZE,
                    "Cannot build on this material.", colour=(255, 30, 50), font_size=12)
            #Returns the original worldmapdict (unedited) if any of the tiles in the coodinates to get built on are non-buildable tiles
            return None
        if coordinate in player_coords_list_to_avoid_building_on: #If player standing on any of the tiles in the coodinates to get built, don't build
            utils.FloatingText(utils.floating_text_group, topleftTile[0] * settings.OVERWORLD_TILE_SIZE, topleftTile[1] * settings.OVERWORLD_TILE_SIZE,
                    "Move player further away from this point.", colour=(255, 30, 100), font_size=12)
            return None
        
        changes.append([coordinate, building_coord_dict[coordinate]])
    for change in changes:
        #Worldmapdict at coordinate equals tile type 
        worldmapdict[change[0]] = change[1]

    #The changed worldmapdict and coordinate changes
    return changes

def add_building_tile_mappings_starting_from_index(tile_mappings_index, maxi, maxj, building_name):
    """Adds a building to the tile mappings dictionary.
    First checks if there is a collision at a tile mapping location.
    This is useful for large buildings (e.g. a 80 x 80px building with 5x5 tiles, needing 25 lines in the dict for individual tiles)
    """
    #Checks if there is a free slot for each piece of a building, and if not a warning is given.
    for dictslot in range(tile_mappings_index, tile_mappings_index + ((maxi + 1) * (maxj + 1))):
        if TILE_MAPPINGS.get(dictslot, "Safe") != "Safe":
            print("There is a collision adding to the Tile Mappings, try again.")
            return

    add_index = tile_mappings_index
    for i in range(0, maxi + 1):
        for j in range(0, maxj + 1):
            TILE_MAPPINGS[add_index] = f"{building_name}{i}{j}"
            add_index += 1

def get_world_tilename_at_xy_from_mappingsdict(xy, overworldmapdict, tile_mappings, tilesize):
    """Gets the tilename at a coordinate based on the map (in dictionary form) and the tile mappings dictionary
    This can be used to check if the map tile is walkable."""
    x = xy[0]
    y = xy[1]
    tilenum = overworldmapdict.get((round(x / tilesize), round(y / tilesize)))
    return tile_mappings[tilenum]

add_building_tile_mappings_starting_from_index(10000, 4, 4, "largeHut")
add_building_tile_mappings_starting_from_index(10100, 4, 5, "shopHut")

overworldmap = []
GRASS_START = 12
GRASS_END = 32
for i in range(0, 40):
    for j in range(0, 40):
        #if (i >= 27 and i <= 29) and (j >= 27 and j <= 29):
        #    overworldmap.append([i, j, 3])
        if (i >= GRASS_START and i <= GRASS_END) and (j >= GRASS_START and j <= GRASS_END):
            overworldmap.append([i, j, 2])

#Overworldmapdict is the ultimate world map. The world map above is just a quick way of initialising. I should rename the above and call the below overworldmap.
default_overworldmapdict = {}
#The format (x, y) = tilenum must be maintained.
worldborderquick = []
for i in range(GRASS_START - 1, GRASS_END + 1 + 1):
    for j in range(GRASS_START - 1, GRASS_END + 1 + 1):
        worldborderquick.append([i, j, 4])

for tile in worldborderquick:
    default_overworldmapdict[(tile[0], tile[1])] = tile[2]

for tile in overworldmap:
    default_overworldmapdict[(tile[0], tile[1])] = tile[2]