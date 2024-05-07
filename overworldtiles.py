import overworldBuildings


def detect_building_worldmap_collision_and_place(worldmapdict, overworldbuilding, topleftTile: tuple) -> dict:
    """Takes the current world map dictionary, a building that is to be built, and the top left tile (that the player is clicking on).
    The building type looks up functions from the overworldbuildings page, and 
    Returns a tile dictionary
    """
    #dynamic method invocation
    building_functions = {
        "smallDungeon": overworldBuildings.get_smallDungeon_tiles
    }
    
    building_function = building_functions.get(overworldbuilding)
    
    if building_function is not None:
        coordDict = building_function(topleftTile)
    else:
        raise ValueError("Unknown building type: {}".format(overworldbuilding))

    for coordinate in coordDict.keys():
        tilenum = worldmapdict.get(coordinate)
        tilename = TILE_MAPPINGS[tilenum]
        if tilename != "overgroundGrass":
            #Returns the original worldmapdict (unedited)
            return worldmapdict
        else:
            worldmapdict[coordinate] = coordDict[coordinate]
    #The changed worldmapdict
    return worldmapdict
    





overworldmap = []
for i in range(0, 40):
    for j in range(0, 40):
        if (i >= 27 and i <= 29) and (j >= 27 and j <= 29):
            overworldmap.append([i, j, 3])
        elif (i >= 15 and i <= 30) and (j >= 15 and j <= 30):
            overworldmap.append([i, j, 2])
        #Defining world border
        elif (i == 0 or j == 0 or i == 39 or j == 39):
            overworldmap.append([i, j, 4])
        else:
            overworldmap.append([i, j, 0])
overworldmap.append([34, 34, 3])

#Overworldmapdict is the ultimate world map. The world map above is just a quick way of initialising. I should rename the above and call the below overworldmap.
overworldmapdict = {}
#The format (x, y) = tilenum must be maintained.
for tile in overworldmap:
    overworldmapdict[(tile[0], tile[1])] = tile[2]

overworldmapdict[(16, 16)] = 5
overworldmapdict[(17, 16)] = 6

overworldmapdict_test = {}
for i in range(0, 100):
    for j in range(0, 100):
        overworldmapdict_test[(i, j)] = 2

TILE_MAPPINGS = {
    0: None,
    1: "overgroundGrid",
    2: "overgroundGrass",
    3: "overgroundWater",
    4: "overgroundBorder",
    5: "overgroundSmallDungeonLeft",
    6: "overgroundSmallDungeonRight"
}


WALKABLE = ["overgroundGrass"]
BUILDABLE = ["overgroundGrass"]

#Gets the tilename at a coordinate based on the map (in dictionary form) and the tile mappings dictionary
#This can be used to check if the map tile is walkable.
def get_world_tilename_at_xy_from_mappingsdict(xy, overworldmapdict, tile_mappings, tilesize):
    x = xy[0]
    y = xy[1]
    tilenum = overworldmapdict.get((round(x / tilesize), round(y / tilesize)))
    return tile_mappings[tilenum]