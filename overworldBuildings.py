def get_smallDungeon_tiles(topleftTile: tuple):
    topleftx = topleftTile[0]
    toplefty = topleftTile[1]
    coordDict = {}
    coordDict[(topleftx, toplefty)] = 5
    coordDict[(topleftx + 1, toplefty)] = 6
    return coordDict