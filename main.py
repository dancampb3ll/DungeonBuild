import pygame
import overworld.tiles
import overworld.buildings
from overworld.player import Player as OverworldPlayer
from overworld.player import TILE_SIZE
from camera import CameraGroup

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
TILE_COUNT = SCREEN_HEIGHT / TILE_SIZE

DEFAULT_NO_TILE_PORTAL = [None, None, None]

class DebugText(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.font_size = 12
        self.font = pygame.font.SysFont("Arial", self.font_size)
        
        self.font_colour = (255, 255, 255)
    

    def update(self, playergridx, playergridy, mapdict, tiledict):
        self.playergridx = playergridx
        self.playergridy = playergridy
        self.tile = mapdict.get((playergridx, playergridy), "error")
        self.material = tiledict.get(self.tile, "Invalid Tile")
        self.text = f"Player x on grid: {self.playergridx} | Player y on grid: {self.playergridy} | Map material at x,y: {self.material}"
        self.image = self.font.render(self.text, True, self.font_colour)
        self.rect = self.image.get_rect(topleft = (5, 5))

class FloatingHud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = "hud"
        self.image = pygame.image.load("assets/hud/hudbar.png").convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH - self.rect.w
        self.rect.y = SCREEN_HEIGHT - self.rect.h

class BuildHud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/hud/buildhudbar.png").convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.x = 2*SCREEN_WIDTH
        self.rect.y = 100
        
    def show(self):
        self.rect.x = SCREEN_WIDTH - self.rect.w

    def hide(self):
        #There must be a better way to do this
        self.rect.x = 2*SCREEN_WIDTH

class CoinText(pygame.sprite.Sprite):
    def __init__(self, hudx, hudy):
        super().__init__()
        self.font_size = 12
        self.font = pygame.font.SysFont("Calibri", self.font_size)
        self.font_colour = (0, 0, 0)
        self.hudx = hudx
        self.hudy = hudy
        self.hud_xoffset = 150
        self.hud_yoffset = 15
        self.coincount = 0
        self.update_coin_display()

    def update_coin_display(self):
        self.text = str(self.coincount)
        self.image = self.font.render(self.text, True, self.font_colour)
        self.rect = self.image.get_rect(topleft = (self.hudx + self.hud_xoffset, self.hudy + self.hud_yoffset))

    def update_coin_count(self, newcoincount):
        self.coincount = newcoincount
        self.update_coin_display()

class ToolTip(pygame.sprite.Sprite):
    def __init__(self, initx, inity, building_type):
        super().__init__()
        self.type = "tooltip"
        self.building_type = building_type
        self.image = pygame.image.load(f"assets/tooltips/{self.building_type}Tooltip.png").convert()
        self.image.set_colorkey((255,0,255))
        self.rect = self.image.get_rect()
        self.rect.x = initx
        self.rect.y = inity
        self.YOFFSET = 20
        self.ABSXOFFSET = 7
        self.tooltipsize = self.rect.width
        self.pos = None

    def update_tooltip_location_from_mouse(self, input_events):
        if self.building_type == "overgroundGrass":
            self.draw_grass_right(input_events)
        else:
            self.draw_building_left(input_events)

    def draw_building_left(self, input_events):
        pos = pygame.mouse.get_pos()
        mousex = pos[0]
        mousey = pos[1]
        self.rect.x = mousex - self.ABSXOFFSET - self.tooltipsize
        self.rect.y = mousey + self.YOFFSET

    def draw_grass_right(self, input_events):
        pos = pygame.mouse.get_pos()
        mousex = pos[0]
        mousey = pos[1]
        self.rect.x = mousex + self.ABSXOFFSET
        self.rect.y = mousey + self.YOFFSET

    def redraw_building_left(self):
        self.image = pygame.image.load(f"assets/tooltips/{self.building_type}Tooltip.png").convert()
        self.image.set_colorkey((255,0,255))

    def update(self):
        self.redraw_building_left()

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption('DungeonBuild')
    pygame.init()

    #Later to be modularised
    pygame.mixer.init()
    pygame.mixer.music.load("assets/music/overworld/Lost-Jungle.mp3")
    pygame.mixer.music.play(-1) #Repeat unlimited
    grass_sfx = pygame.mixer.Sound("assets/sfx/GrassPlacement.mp3")
    building_sfx = pygame.mixer.Sound("assets/sfx/BuildingPlacement.mp3")

    def build_and_perform_tiledict_spritedict_updates(mapdict, structuretype, topleftplacementcoord: tuple, player_coords_list_to_avoid_building_on=[None]):
        """Gets the world map, looks where the structure is to be built, and if possible deletes sprites from the spritedict.
        Returns the new world map dict with new buildings as replacements for old.
        """
        if topleftplacementcoord == None:
            return mapdict

        newmap, changes = overworld.tiles.detect_building_worldmap_collision_place_and_changes(mapdict, structuretype, topleftplacementcoord, player_coords_list_to_avoid_building_on)
        if changes == None:
            return mapdict
        #A change is given in format [(x,y), tilenum]
        for change in changes:
            x = change[0][0]
            y = change[0][1]
            tilenum = change[1]
            tilename = tile_mappings[tilenum]
            #Kills the original sprite before generating a new tile to replace it.
            spriteDict[(x, y)].kill()
            #Creates an instance of the new tile.
            spriteDict[(x, y)] = overworld.tiles.OutdoorTile(x, y, tilename, cameragroup, DEFAULT_NO_TILE_PORTAL)
        building_sfx.play()
        return newmap

    def draw_new_border_tiles_from_grass_placement(mapdict, placementx, placementy):
        for adjacentoffset in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
            checkx = placementx + adjacentoffset[0]
            checky = placementy + adjacentoffset[1]

            check_sprite = spriteDict.get((checkx, checky), None)
            if check_sprite is None:
                spriteDict[(checkx, checky)] = overworld.tiles.OutdoorTile(checkx, checky, "overgroundBorder", cameragroup, DEFAULT_NO_TILE_PORTAL)
                mapdict[(checkx, checky)] = 4

    def build_grass_block_and_perform_tile_sprite_updates(mapdict, placementcoord):
        if placementcoord is None:
            return mapdict
        x = placementcoord[0]
        y = placementcoord[1]
        tile_sprite = spriteDict.get((x,y), None)
        if tile_sprite is None:
            return mapdict
        if tile_sprite.tile != "overgroundBorder":
            return mapdict
        spriteDict[(x, y)].kill()
        spriteDict[(x, y)] = overworld.tiles.OutdoorTile(x, y, "overgroundGrass", cameragroup, DEFAULT_NO_TILE_PORTAL)
        draw_new_border_tiles_from_grass_placement(mapdict, x, y)
        grass_sfx.play()
        mapdict[(x, y)] = 2

        return mapdict

    def check_buildmode_and_update_tooltips(player_buildmode, player_selected_building, leftTT, rightTT, input_events):
        if not player_buildmode:
            for tooltip in building_tooltips:
                tooltip.kill()
            return None, None
        if len(building_tooltips) == 2:
            leftTT.update_tooltip_location_from_mouse(input_events)
            rightTT.update_tooltip_location_from_mouse(input_events)
            return leftTT, rightTT
        else:
            #Making new tooltips:
            leftTT = ToolTip(-999, -999, player_selected_building)
            rightTT = ToolTip(-999, -999, "overgroundGrass")
            building_tooltips.add(leftTT)
            building_tooltips.add(rightTT)
            return leftTT, rightTT

    #Camera must be defined first
    cameragroup = CameraGroup()

    #HUD is separate from the camera
    hud = pygame.sprite.Group()
    hudbar = FloatingHud()
    cointext = CoinText(hudbar.rect.topleft[0], hudbar.rect.topleft[1])
    buildhud = BuildHud()
    hud.add(hudbar)
    hud.add(cointext)
    hud.add(buildhud)

    #Drawing tiles
    overworldmapdict = overworld.tiles.overworldmapdict
    tile_mappings = overworld.tiles.TILE_MAPPINGS

    #Used to maintain sprites at given locations.
    spriteDict = {}

    #Map initialisation - creates sprites for tiles that aren't blanks (value 0)
    #Need to make this a general adding block function
    for coord in overworldmapdict.keys():
        x = coord[0]
        y = coord[1]
        tiletype = overworldmapdict[(x, y)]
        if tiletype != 0:
            tilename = tile_mappings[tiletype]
            spriteDict[(x, y)] = overworld.tiles.OutdoorTile(x, y, tilename, cameragroup, DEFAULT_NO_TILE_PORTAL)

    #Temporary test for making portal work
    build_and_perform_tiledict_spritedict_updates(overworldmapdict, "smallDungeon", (20, 20))
    spriteDict.get((20, 20)).portal_type = "dungeon"
    spriteDict.get((20, 20)).portal_destination = (27, 27) # Can't access from here?
    spriteDict.get((20, 20)).portal_collision_side = "bottom"


    player = OverworldPlayer(cameragroup)

    debugtext = DebugText()
    screentext = pygame.sprite.Group()
    screentext.add(debugtext)

    building_tooltips = pygame.sprite.Group()
    tooltip_left = None
    tooltip_right = None

    mainloop = True
    selected_world = "overworld"
    while mainloop:
        while selected_world == "overworld":
            input_events = pygame.event.get()
            for event in input_events:
                if event.type == pygame.QUIT:
                    mainloop = False
            screen.fill((10, 10, 18))

            #Cameragroup contains tile sprites, which are used to detect collisions.
            player.move_player(cameragroup)
            player.check_build_mode(input_events, buildhud, cameragroup)
            player.custom_update(input_events, tooltip_left)

            #If none returned from get coords, nothing is changed on overworldmap dict
            player_building_placement_coords_topleft = player.place_building_get_coords(input_events, cameragroup)
            player_corner_coords_list = player.get_player_corner_grid_locations()
            overworldmapdict = build_and_perform_tiledict_spritedict_updates(overworldmapdict, player.selected_building, player_building_placement_coords_topleft, player_corner_coords_list)

            #If none returned from get coords, nothing is changed on overworldmap dict
            player_Grass_placement_coords = player.place_grass_block_get_coords(input_events, cameragroup)
            overworldmapdict = build_grass_block_and_perform_tile_sprite_updates(overworldmapdict, player_Grass_placement_coords)

            cameragroup.remove(player)
            cameragroup.add(player)
            cameragroup.update()
            cameragroup.custom_draw(player)

            debugtext.update(player.gridx, player.gridy, overworldmapdict, tile_mappings)
            screentext.draw(screen)

            tooltip_left, tooltip_right = check_buildmode_and_update_tooltips(player.buildmode, player.selected_building, tooltip_left, tooltip_right, input_events) #Make largeHut dependent on player selected material

            hud.draw(screen)

            building_tooltips.update()
            building_tooltips.draw(screen)

            selected_world = player.gameworld
            pygame.display.update()
            clock.tick(60)

        while selected_world == "dungeon":
            input_events = pygame.event.get()
            for event in input_events:
                if event.type == pygame.QUIT:
                    mainloop = False
            screen.fill((0, 0, 0))
            pygame.display.update()
            clock.tick(60)

if __name__ == "__main__":
    main()