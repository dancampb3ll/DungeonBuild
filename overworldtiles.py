overworldmap = []
for i in range(0, 40):
    for j in range(0, 40):
        if (i >= 27 and i <= 29) and (j >= 27 and j <= 29):
            overworldmap.append([i, j, 3])
        elif (i >= 15 and i <= 30) and (j >= 15 and j <= 30):
            overworldmap.append([i, j, 2])
        else:
            overworldmap.append([i, j, 0])
overworldmap.append([34, 34, 3])

#Overworldmapdict is the ultimate world map. The world map above is just a quick way of initialising. I should rename the above and call the below overworldmap.
overworldmapdict = {}
for tile in overworldmap:
    overworldmapdict[(tile[0], tile[1])] = tile[2]

tile_mappings = {
    0: None,
    1: "overgroundGrid",
    2: "overgroundGrass",
    3: "overgroundWater"
}

walkable = ["overgroundGrass"]

def get_world_tilename_at_xy_from_mappingsdict(xy, overworldmapdict, tile_mappings, tilesize):
    x = xy[0]
    y = xy[1]
    tilenum = overworldmapdict.get((round(x / tilesize), round(y / tilesize)))
    return tile_mappings[tilenum]