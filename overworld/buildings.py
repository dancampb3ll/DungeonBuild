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
    #Adding fence
    coordDict[(topleftx - 1, toplefty - 1)] = 8
    coordDict[(topleftx, toplefty - 1)] = 9
    coordDict[(topleftx + 1, toplefty - 1)] = 9
    coordDict[(topleftx + 2, toplefty - 1)] = 10
    coordDict[(topleftx - 1, toplefty + 0)] = 11
    coordDict[(topleftx - 1, toplefty + 1)] = 11
    coordDict[(topleftx - 1, toplefty + 2)] = 11
    coordDict[(topleftx + 2, toplefty + 0)] = 12
    coordDict[(topleftx + 2, toplefty + 1)] = 12
    coordDict[(topleftx + 2, toplefty + 2)] = 12
    
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

def get_tinyPot_tiles(topleftTile: tuple):
    topleftx = topleftTile[0]
    toplefty = topleftTile[1]
    coordDict = {}
    coordDict[(topleftx, toplefty)] = 7
    return coordDict

def get_tinyFlower_tiles(topleftTile: tuple):
    topleftx = topleftTile[0]
    toplefty = topleftTile[1]
    coordDict = {}
    coordDict[(topleftx, toplefty)] = 16
    return coordDict

def get_cobblestone_tiles(topleftTile: tuple):
    topleftx = topleftTile[0]
    toplefty = topleftTile[1]
    coordDict = {}
    coordDict[(topleftx, toplefty)] = 17
    return coordDict

def get_shopHut_tiles(topleftTile: tuple):
    topleftx = topleftTile[0]
    toplefty = topleftTile[1]
    BUILDINGSIZEX = 5
    BUILDINGSIZEY = 6
    INDEXSTART = 10100

    coordDict = {}
    tile_index_offset = 0
    for i in range(0, BUILDINGSIZEX):
        for j in range(0, BUILDINGSIZEY):
            coordDict[(topleftx + i, toplefty + j)] = INDEXSTART + tile_index_offset
            tile_index_offset += 1
    return coordDict

#Keeps a list of all building functions by building name, so they can be referenced by simple name within overworld.tiles 
building_functions = {
        "smallDungeon": get_smallDungeon_tiles,
        "largeHut": get_largeHut_tiles,
        "tinyPot": get_tinyPot_tiles,
        "tinyFlower": get_tinyFlower_tiles,
        "shopHut": get_shopHut_tiles,
        "cobblestone": get_cobblestone_tiles
    }

BUILDING_TYPES = [key for key in building_functions.keys()]