import overworldBuildings

WALKABLE = ["overgroundGrass"]
BUILDABLE = ["overgroundGrass"]
TILE_MAPPINGS = {
    0: None,
    1: "overgroundGrid",
    2: "overgroundGrass",
    3: "overgroundWater",
    4: "overgroundBorder",
    5: "overgroundSmallDungeonLeft",
    6: "overgroundSmallDungeonRight"
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
        coordDict = building_function(topleftTile)
    else:
        raise ValueError("Unknown building type: {}".format(overworldbuilding))

    changes = []
    for coordinate in coordDict.keys():
        tilenum = worldmapdict.get(coordinate)
        tilename = TILE_MAPPINGS[tilenum]
        if tilename != "overgroundGrass":
            #Returns the original worldmapdict (unedited)
            return worldmapdict, None
        else:
            worldmapdict[coordinate] = coordDict[coordinate]
            changes.append([coordinate, coordDict[coordinate]])
    #The changed worldmapdict and coordinate changes
    return worldmapdict, changes

overworldmap = []
for i in range(0, 40):
    for j in range(0, 40):
        if (i >= 27 and i <= 29) and (j >= 27 and j <= 29):
            overworldmap.append([i, j, 3])
        elif (i >= 15 and i <= 30) and (j >= 15 and j <= 30):
            overworldmap.append([i, j, 2])
        #Defining world border
        elif (i == 14 or j == 14 or i == 31 or j == 31):
            overworldmap.append([i, j, 4])
overworldmap.append([34, 34, 3])

#Overworldmapdict is the ultimate world map. The world map above is just a quick way of initialising. I should rename the above and call the below overworldmap.
overworldmapdict = {}
#The format (x, y) = tilenum must be maintained.
for tile in overworldmap:
    overworldmapdict[(tile[0], tile[1])] = tile[2]

overworldmapdict[(16, 16)] = 5
overworldmapdict[(17, 16)] = 6



#Gets the tilename at a coordinate based on the map (in dictionary form) and the tile mappings dictionary
#This can be used to check if the map tile is walkable.
def get_world_tilename_at_xy_from_mappingsdict(xy, overworldmapdict, tile_mappings, tilesize):
    x = xy[0]
    y = xy[1]
    tilenum = overworldmapdict.get((round(x / tilesize), round(y / tilesize)))
    return tile_mappings[tilenum]