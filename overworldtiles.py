import overworldBuildings

"""
This tab defines tile mappings, their properties such as building buildable, 
"""

WALKABLE = ["overgroundGrass"]
BUILDABLE = ["overgroundGrass"]
TILE_MAPPINGS = {
    0: None,
    1: "overgroundGrid",
    2: "overgroundGrass",
    3: "overgroundWater",
    4: "overgroundBorder",
    5: "overgroundSmallDungeonLeft",
    6: "overgroundSmallDungeonRight",
    7: "tinyPot"
}

def detect_building_worldmap_collision_place_and_changes(worldmapdict, overworldbuilding, topleftTile: tuple) -> dict:
    """Takes the current world map dictionary, a building that is to be built, and the top left tile (that the player is clicking on).
    The building type looks up functions from the overworldbuildings page, and 
    Returns a tile dictionary, coordinate changes. A change is given in format [(x,y), changenum]
    """
    #dynamic method invocation
    building_functions = overworldBuildings.building_functions
    
    building_function = building_functions.get(overworldbuilding)

    if building_function is not None:
        building_coord_dict = building_function(topleftTile)
    else:
        raise ValueError("Unknown building type: {}".format(overworldbuilding))

    changes = []
    for coordinate in building_coord_dict.keys():
        tilenum = worldmapdict.get(coordinate)
        tilename = TILE_MAPPINGS[tilenum]
        if tilename != "overgroundGrass":
            #Returns the original worldmapdict (unedited)
            return worldmapdict, None
        else:
            changes.append([coordinate, building_coord_dict[coordinate]])
    for change in changes:
        #Worldmapdict at coordinate equals tile type 
        worldmapdict[change[0]] = change[1]

    #The changed worldmapdict and coordinate changes
    return worldmapdict, changes

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

overworldmap = []
for i in range(0, 40):
    for j in range(0, 40):
        if (i >= 27 and i <= 29) and (j >= 27 and j <= 29):
            overworldmap.append([i, j, 3])
        elif (i >= 15 and i <= 30) and (j >= 15 and j <= 30):
            overworldmap.append([i, j, 2])

#Overworldmapdict is the ultimate world map. The world map above is just a quick way of initialising. I should rename the above and call the below overworldmap.
overworldmapdict = {}
#The format (x, y) = tilenum must be maintained.
worldborderquick = []
for i in range(14, 32):
    for j in range(14, 32):
        worldborderquick.append([i, j, 4])

for tile in worldborderquick:
    overworldmapdict[(tile[0], tile[1])] = tile[2]

for tile in overworldmap:
    overworldmapdict[(tile[0], tile[1])] = tile[2]

