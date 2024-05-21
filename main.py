import pygame
import overworld.tiles
import overworld.buildings
import settings
import hud

from overworld.player import Player as OverworldPlayer
from camera import CameraGroup

TILE_COUNT = settings.SCREEN_HEIGHT / settings.TILE_SIZE

DEFAULT_NO_TILE_PORTAL = [None, None, None]

class GameState():
    def __init__(self):
        self.overworld_map_dict = overworld.tiles.overworldmapdict


def main():
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption('DungeonBuild')
    pygame.init()

    #Later to be modularised
    pygame.mixer.init()
    pygame.mixer.music.load("assets/music/overworld/Lost-Jungle.mp3")
    pygame.mixer.music.play(-1) #Repeat unlimited
    grass_sfx = pygame.mixer.Sound("assets/sfx/GrassPlacement.mp3")
    building_sfx = pygame.mixer.Sound("assets/sfx/BuildingPlacement.mp3")

    def build_and_perform_tiledict_spritedict_updates(mapdict, structuretype, topleftplacementcoord: tuple, player_coords_list_to_avoid_building_on=[None], play_sfx = False):
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
        if play_sfx:
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
            leftTT = hud.ToolTip(-999, -999, player_selected_building)
            rightTT = hud.ToolTip(-999, -999, "overgroundGrass")
            building_tooltips.add(leftTT)
            building_tooltips.add(rightTT)
            return leftTT, rightTT

    gamestate = GameState()

    #Camera must be the first Pygame object defined.
    cameragroup = CameraGroup()

    #HUD is separate from the camera
    hudgroup = pygame.sprite.Group()
    hudbar = hud.FloatingHud()
    cointext = hud.CoinText(hudbar.rect.topleft[0], hudbar.rect.topleft[1])
    buildhud = hud.BuildHud()
    hudgroup.add(hudbar)
    hudgroup.add(cointext)
    hudgroup.add(buildhud)

    #Drawing tiles
    overworld_map_dict = gamestate.overworld_map_dict
    tile_mappings = overworld.tiles.TILE_MAPPINGS

    #Used to maintain sprites at given locations.
    spriteDict = {}

    #Map initialisation - creates sprites for tiles that aren't blanks (value 0)
    #Need to make this a general adding block function
    for coord in overworld_map_dict.keys():
        x = coord[0]
        y = coord[1]
        tiletype = overworld_map_dict[(x, y)]
        if tiletype != 0:
            tilename = tile_mappings[tiletype]
            spriteDict[(x, y)] = overworld.tiles.OutdoorTile(x, y, tilename, cameragroup, DEFAULT_NO_TILE_PORTAL)

    #Temporary test for making portal work
    build_and_perform_tiledict_spritedict_updates(overworld_map_dict, "smallDungeon", (20, 20))
    spriteDict.get((20, 20)).portal_type = "dungeon"
    spriteDict.get((20, 20)).portal_destination = (27, 27) # Can't access from here?
    spriteDict.get((20, 20)).portal_collision_side = "bottom"
    player = OverworldPlayer(cameragroup)

    debugtext = hud.DebugText()
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
            build_and_perform_tiledict_spritedict_updates(overworld_map_dict, player.selected_building, player_building_placement_coords_topleft, player_corner_coords_list, True)

            #If none returned from get coords, nothing is changed on overworldmap dict
            player_Grass_placement_coords = player.place_grass_block_get_coords(input_events, cameragroup)
            build_grass_block_and_perform_tile_sprite_updates(overworld_map_dict, player_Grass_placement_coords)

            cameragroup.remove(player)
            cameragroup.add(player)
            cameragroup.update()
            cameragroup.custom_draw(player)

            debugtext.update(player.gridx, player.gridy, overworld_map_dict, tile_mappings)
            screentext.draw(screen)

            tooltip_left, tooltip_right = check_buildmode_and_update_tooltips(player.buildmode, player.selected_building, tooltip_left, tooltip_right, input_events) #Make largeHut dependent on player selected material

            hudgroup.draw(screen)

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