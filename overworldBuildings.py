def get_Grass_tiles(topleftTile: tuple):
    topleftx = topleftTile[0]
    toplefty = topleftTile[1]
    coordDict = {}
    coordDict[(topleftx, toplefty)] = 2
    return coordDict

def get_smallDungeon_tiles(topleftTile: tuple):
    topleftx = topleftTile[0]
    toplefty = topleftTile[1]
    coordDict = {}
    coordDict[(topleftx, toplefty)] = 5
    coordDict[(topleftx + 1, toplefty)] = 6
    return coordDict

def get_largeHut_tiles(topleftTile: tuple):
    topleftx = topleftTile[0]
    toplefty = topleftTile[1]
    BUILDINGSIZE = 5
    INDEXSTART = 10000

    coordDict = {}
    tile_index_offset = 0
    for i in range(0, BUILDINGSIZE):
        for j in range(0, BUILDINGSIZE):
            coordDict[(topleftx + i, toplefty + j)] = INDEXSTART + tile_index_offset
            tile_index_offset += 1
    return coordDict


#Keeps a list of all building functions by building name, so they can be referenced by simple name within overworldTiles 
building_functions = {
        "Grass": get_Grass_tiles,
        "smallDungeon": get_smallDungeon_tiles,
        "largeHut": get_largeHut_tiles
    }