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
    coordDict = None #Not yet built
    return coordDict


building_functions = {
        "Grass": get_Grass_tiles,
        "smallDungeon": get_smallDungeon_tiles,
        "mediumHut": get_largeHut_tiles
    }