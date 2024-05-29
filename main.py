import pygame
import overworld.tiles
import overworld.buildings
import underworld.tiles
import underworld.player
import underworld.npc
import settings
import hud
from overworld.player import Player as OverworldPlayer
from camera import CameraGroup


TILE_COUNT = settings.SCREEN_HEIGHT / settings.OVERWORLD_TILE_SIZE
DEFAULT_NO_TILE_PORTAL = [None, None, None]

class GameState():
    def __init__(self):
        self.overworld_map_dict = overworld.tiles.overworldmapdict
        self.sprite_dict = {}
        self.overworldcamera = CameraGroup()
        self.underworldcamera = CameraGroup()
        self.current_music = None

    def update_current_music(self, track):
        self.current_music = track

def build_and_perform_tiledict_spritedict_updates(gamestate, structuretype, topleftplacementcoord: tuple, player_coords_list_to_avoid_building_on=[None], play_sfx = False):
        """Gets the world map, looks where the structure is to be built, and if possible deletes sprites from the spritedict.
        Returns the new world map dict with new buildings as replacements for old.
        """
        if topleftplacementcoord == None:
            return

        changes = overworld.tiles.detect_building_worldmap_collision_place_and_changes(gamestate.overworld_map_dict, structuretype, topleftplacementcoord, player_coords_list_to_avoid_building_on)
        if changes == None:
            return
        #A change is given in format [(x,y), tilenum]
        for change in changes:
            x = change[0][0]
            y = change[0][1]
            tilenum = change[1]
            tilename = overworld.tiles.TILE_MAPPINGS[tilenum]
            #Kills the original sprite before generating a new tile to replace it.
            gamestate.sprite_dict[(x, y)].kill()
            #Creates an instance of the new tile.
            gamestate.sprite_dict[(x, y)] = overworld.tiles.OutdoorTile(x, y, tilename, gamestate.overworldcamera, DEFAULT_NO_TILE_PORTAL)
        if play_sfx:
            play_sfx.play()
        return


def draw_new_border_tiles_from_grass_placement(gamestate, placementx, placementy):
    for adjacentoffset in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
        checkx = placementx + adjacentoffset[0]
        checky = placementy + adjacentoffset[1]

        check_sprite = gamestate.sprite_dict.get((checkx, checky), None)
        if check_sprite is None:
            gamestate.sprite_dict[(checkx, checky)] = overworld.tiles.OutdoorTile(checkx, checky, "overgroundBorder", gamestate.overworldcamera, DEFAULT_NO_TILE_PORTAL)
            gamestate.overworld_map_dict[(checkx, checky)] = 4


def build_grass_block_and_perform_tile_sprite_updates(gamestate, placementcoord, play_sfx = None):
    if placementcoord is None:
        return
    x = placementcoord[0]
    y = placementcoord[1]
    tile_sprite = gamestate.sprite_dict.get((x,y), None)
    if tile_sprite is None:
        return
    if tile_sprite.tile != "overgroundBorder":
        return
    gamestate.sprite_dict[(x, y)].kill()
    gamestate.sprite_dict[(x, y)] = overworld.tiles.OutdoorTile(x, y, "overgroundGrass", gamestate.overworldcamera, DEFAULT_NO_TILE_PORTAL)
    draw_new_border_tiles_from_grass_placement(gamestate, x, y)
    gamestate.overworld_map_dict[(x, y)] = 2
    if play_sfx:
        play_sfx.play()
    return


def check_buildmode_and_update_tooltips(player_buildmode, player_selected_building, leftTT, rightTT, input_events, building_tooltips_group):
    if not player_buildmode:
        for tooltip in building_tooltips_group:
            tooltip.kill()
        return None, None
    if len(building_tooltips_group) == 2:
        leftTT.update_tooltip_location_from_mouse(input_events)
        rightTT.update_tooltip_location_from_mouse(input_events)
        return leftTT, rightTT
    else:
        #Making new tooltips:
        leftTT = hud.ToolTip(-999, -999, player_selected_building)
        rightTT = hud.ToolTip(-999, -999, "overgroundGrass")
        building_tooltips_group.add(leftTT)
        building_tooltips_group.add(rightTT)
        return leftTT, rightTT


def main():
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption('DungeonBuild')
    pygame.init()

    #Later to be modularised
    pygame.mixer.init()
    pygame.mixer.music.load("assets/music/overworld/Lost-Jungle.mp3")
    pygame.mixer.music.play(-1) #Repeat unlimited
    GRASS_SFX = pygame.mixer.Sound("assets/sfx/GrassPlacement.mp3")
    BUILDING_SFX = pygame.mixer.Sound("assets/sfx/BuildingPlacement.mp3")

    gamestate = GameState()
    gamestate.current_music = "assets/music/overworld/Lost-Jungle.mp3"
    #Camera must be the first Pygame object defined.
    overworldcamera = gamestate.overworldcamera
    underworldcamera = gamestate.underworldcamera
    for i in range(0, 15):
        for j in range(0, 15):
            underworld.tiles.UnderworldTile(i, j, "cobblestone", underworldcamera, DEFAULT_NO_TILE_PORTAL)


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

    #Used to maintain sprites at given locations.
    gamestate.sprite_dict = gamestate.sprite_dict

    #Map initialisation - creates sprites for tiles that aren't blanks (value 0)
    #Need to make this a general adding block function
    for coord in overworld_map_dict.keys():
        x = coord[0]
        y = coord[1]
        tiletype = overworld_map_dict[(x, y)]
        if tiletype != 0:
            tilename = overworld.tiles.TILE_MAPPINGS[tiletype]
            gamestate.sprite_dict[(x, y)] = overworld.tiles.OutdoorTile(x, y, tilename, overworldcamera, DEFAULT_NO_TILE_PORTAL)

    #Temporary test for making portal work
    build_and_perform_tiledict_spritedict_updates(gamestate, "smallDungeon", (20, 20))
    gamestate.sprite_dict.get((20, 20)).portal_type = "underworld"
    gamestate.sprite_dict.get((20, 20)).portal_destination = (27, 27) # Can't access from here?
    gamestate.sprite_dict.get((20, 20)).portal_collision_side = "bottom"
    player = OverworldPlayer(overworldcamera)
    underworldplayer = underworld.player.Player(underworldcamera)

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
            

            #overworldcamera contains tile sprites, which are used to detect collisions.
            player.move_player(overworldcamera)
            player.check_build_mode(input_events, buildhud, overworldcamera)
            player.custom_update(input_events, tooltip_left)

            #If none returned from get coords, nothing is changed on overworldmap dict
            player_building_placement_coords_topleft = player.place_building_get_coords(input_events, overworldcamera)
            player_corner_coords_list = player.get_player_corner_grid_locations()
            build_and_perform_tiledict_spritedict_updates(gamestate, player.selected_building, player_building_placement_coords_topleft, player_corner_coords_list, BUILDING_SFX)

            #If none returned from get coords, nothing is changed on overworldmap dict
            player_Grass_placement_coords = player.place_grass_block_get_coords(input_events, overworldcamera)
            build_grass_block_and_perform_tile_sprite_updates(gamestate, player_Grass_placement_coords, GRASS_SFX)

            #Moves player to front in case of new blocks being built (which are automatically appended to the end of the group)
            overworldcamera.remove(player)
            overworldcamera.add(player)
            #*********************

            overworldcamera.update()
            overworldcamera.custom_draw(player)

            debugtext.update(player.gridx, player.gridy, overworld_map_dict, overworld.tiles.TILE_MAPPINGS)
            screentext.draw(screen)

            tooltip_left, tooltip_right = check_buildmode_and_update_tooltips(player.buildmode, player.selected_building, tooltip_left, tooltip_right, input_events, building_tooltips)

            hudgroup.draw(screen)

            building_tooltips.update()
            building_tooltips.draw(screen)

            selected_world = player.gameworld
            pygame.display.update()
            clock.tick(60)

        slime = underworld.npc.Slime(underworldcamera, 50, 50)
        dagger = underworld.player.Weapon(underworldcamera, "dagger")
        while selected_world == "underworld":
            input_events = pygame.event.get()
            for event in input_events:
                if event.type == pygame.QUIT:
                    mainloop = False
                    selected_world = False

            underworld_track = "assets/music/underworld/Realm-of-Fantasy.mp3"
            if gamestate.current_music != underworld_track:
                pygame.mixer.music.load(underworld_track)
                pygame.mixer.music.play(-1) #Repeat unlimited
            gamestate.update_current_music(underworld_track)
            screen.fill((0, 0, 0))

            underworldplayer.move_player(underworldcamera)
            underworldplayer.custom_update()

            dagger.update_weapon_position(underworldplayer.rect, underworldplayer.facing_direction, underworldplayer.is_moving_x, underworldplayer.is_moving_y)

            #Moves player to front in case of new blocks being built (which are automatically appended to the end of the group)
            underworldcamera.remove(underworldplayer)
            underworldcamera.add(underworldplayer)
            #*********************

            underworldcamera.update()
            underworldcamera.custom_draw(underworldplayer)
            
            dagger.update_attack_hitbox_and_detect_collisions(screen, underworldcamera, underworldplayer.rect, underworldplayer.facing_direction, input_events)
            dagger.detect_enemy_weapon_collision(underworldcamera)
            pygame.display.update()
            clock.tick(60)

if __name__ == "__main__":
    main()