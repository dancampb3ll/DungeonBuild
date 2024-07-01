import pygame
import overworld.tiles
import overworld.buildings
import underworld.tiles
import underworld.player
import underworld.npc
import settings
import hud
import math
from overworld.player import Player as OverworldPlayer
from camera import CameraGroup


TILE_COUNT = settings.SCREEN_HEIGHT / settings.OVERWORLD_TILE_SIZE
DEFAULT_NO_TILE_PORTAL = [None, None, None]

class GameState():
    def __init__(self):
        self.overworld_map_dict = overworld.tiles.overworldmapdict
        self.sprite_dict = {}
        self.overworldcamera = CameraGroup()
        self.overworld_coincount = 0
        self.underworldcamera = CameraGroup()
        self.current_music = None
        self.underworld_map_dict = {}
        self.underworld_npc_spawn_dict = {}
        self.underworld_tile_sprite_dict = {}
        self.underworld_todraw_tile_dict = {}
        self.selected_world = "overworld"

    def update_current_music(self, track):
        self.current_music = track

    def generate_underworld_dungeon_and_update_map(self):
        self.underworld_map_dict, self.underworld_npc_spawn_dict = underworld.tiles.generate_new_map_dict_and_spawns()
    
    def spawn_enemies_from_spawn_dict(self, sprite_group):
        for coord in self.underworld_npc_spawn_dict:
            enemy_type = self.underworld_npc_spawn_dict[coord]
            underworld.npc.Npc(sprite_group, coord[0], coord[1], enemy_type)

    def update_sprite_dict_and_drawn_map(self, camera_group, player_center):
        map = self.underworld_map_dict
        def calculate_distance_pythagoras(point1: tuple, point2: tuple):
            x1, y1 = point1
            x2, y2 = point2
            return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        def determine_to_draw_dict(self, camera_group, player_center):
            player_gridx = player_center[0] // settings.UNDERWORLD_TILE_SIZE
            player_gridy = player_center[1] // settings.UNDERWORLD_TILE_SIZE
            self.underworld_todraw_tile_dict = {}
            for coord in map.keys():
                gridx = coord[0]
                gridy = coord[1]
                distance = calculate_distance_pythagoras((gridx, gridy), (player_gridx, player_gridy))
                if distance < settings.UNDERWORLD_DRAW_DISTANCE:
                    self.underworld_todraw_tile_dict[(gridx, gridy)] = True

        determine_to_draw_dict(self, camera_group, player_center)

        for coord in map.keys():
            gridx = coord[0]
            gridy = coord[1]
            material = map[coord][0]
            portal = map[coord][1]
            #Handling tiles to draw not in current sprite dict
            #print(self.underworld_todraw_tile_dict.get((0, 0), "Not in to draw"))
            #print(self.underworld_tile_sprite_dict.get((0, 0), "Undrawn"))
            if self.underworld_todraw_tile_dict.get(coord, False) == True:
                if self.underworld_tile_sprite_dict.get(coord, False) == False:
                    self.underworld_tile_sprite_dict[(gridx, gridy)] = underworld.tiles.UnderworldTile(gridx, gridy, material, camera_group, portal, player_center)
            else:
                if self.underworld_tile_sprite_dict.get(coord, False) != False:
                    self.underworld_tile_sprite_dict[(gridx, gridy)].kill()
                    del self.underworld_tile_sprite_dict[(gridx, gridy)]

    def clear_underworld_gamestate(self):
        self.underworld_map_dict = {}
        self.underworld_npc_spawn_dict = {}
        self.underworld_tile_sprite_dict = {}
        self.underworld_todraw_tile_dict = {}

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
            #Creates an instance of the new tile
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

def reset_underworld_groups():
    underworld.npc.enemy_group = pygame.sprite.Group()
    underworld.npc.projectile_group = pygame.sprite.Group()
    underworld.npc.coin_group = pygame.sprite.Group()
    underworld.npc.coin_drop_text_group = pygame.sprite.Group()

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

def refresh_underworld_draw_order(camera_group, player):
    #Drawn from lowest priority to max
    if player.facing_direction == "down":
        draw_order = ["tile", "npc", "player", "weapon", "coin", "projectile", "coinDropText"]
    else:
        draw_order = ["tile", "npc", "weapon", "player", "coin", "projectile", "coinDropText"]

    for sprite_type in draw_order:
        for sprite in camera_group.sprites():
            if sprite.type == sprite_type:    
                camera_group.remove(sprite)
                camera_group.add(sprite)

def main():
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption('DungeonBuild')
    pygame.init()

    #Later to be modularised
    pygame.mixer.init()
    overworld_track = "assets/music/overworld/Lost-Jungle.mp3"
    pygame.mixer.music.load(overworld_track)
    pygame.mixer.music.play(-1) #Repeat unlimited
    GRASS_SFX = pygame.mixer.Sound("assets/sfx/GrassPlacement.mp3")
    BUILDING_SFX = pygame.mixer.Sound("assets/sfx/BuildingPlacement.mp3")

    gamestate = GameState()
    gamestate.current_music = "assets/music/overworld/Lost-Jungle.mp3"
    #Camera must be the first Pygame object defined.
    overworldcamera = gamestate.overworldcamera

    #HUD is separate from the camera
    overworld_hudgroup = pygame.sprite.Group()
    overworld_hudbar = hud.OverworldHud()
    overworld_cointext = hud.OverworldCoinText(overworld_hudbar.rect.topleft[0], overworld_hudbar.rect.topleft[1], gamestate.overworld_coincount)
    buildhud = hud.BuildHud()
    overworld_hudgroup.add(overworld_hudbar)
    overworld_hudgroup.add(overworld_cointext)
    overworld_hudgroup.add(buildhud)

    underworld_hudgroup = pygame.sprite.Group()

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
    

    debugtext = hud.DebugText()
    screentext = pygame.sprite.Group()
    screentext.add(debugtext)

    building_tooltips = pygame.sprite.Group()
    tooltip_left = None
    tooltip_right = None

    mainloop = True
    while mainloop:
        gamestate.clear_underworld_gamestate()
        player = OverworldPlayer(overworldcamera)
        while gamestate.selected_world == "overworld":
            input_events = pygame.event.get()
            for event in input_events:
                if event.type == pygame.QUIT:
                    mainloop = False
            if gamestate.current_music != overworld_track:
                pygame.mixer.music.load(overworld_track)
                pygame.mixer.music.play(-1) #Repeat unlimited
            gamestate.update_current_music(overworld_track)
            screen.fill((10, 10, 18))
            
            overworld_cointext.update_coin_count(gamestate.overworld_coincount)



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

            overworld_hudgroup.draw(screen)

            building_tooltips.update()
            building_tooltips.draw(screen)

            gamestate.selected_world = player.gameworld
            pygame.display.update()
            clock.tick(60)
        player.kill()


        #Pre-Underworld Loop initialisation ************
        gamestate.underworldcamera = CameraGroup()
        underworldcamera = gamestate.underworldcamera

        gamestate.generate_underworld_dungeon_and_update_map()
        
        reset_underworld_groups()
        enemy_group = underworld.npc.enemy_group
        coin_group = underworld.npc.coin_group
        projectile_group = underworld.npc.projectile_group
        coin_drop_text_group = underworld.npc.coin_drop_text_group

        gamestate.spawn_enemies_from_spawn_dict(enemy_group)
        dagger = underworld.player.Weapon(underworldcamera, "dagger")
        underworldplayer = underworld.player.Player(underworldcamera)
        underworld_track = "assets/music/underworld/Realm-of-Fantasy.mp3"
        underworld_hudbar = hud.UnderworldHud()
        underworld_hudgroup.add(underworld_hudbar)

        enemy_count = len(enemy_group)
        enemies_killed = 0
        while gamestate.selected_world == "underworld":
            input_events = pygame.event.get()
            for event in input_events:
                if event.type == pygame.QUIT:
                    mainloop = False
                    selected_world = False


            if gamestate.current_music != underworld_track:
                pygame.mixer.music.load(underworld_track)
                pygame.mixer.music.play(-1) #Repeat unlimited
            gamestate.update_current_music(underworld_track)
            screen.fill((0, 0, 0))

            underworldplayer.move_player(underworldcamera, gamestate.underworld_map_dict)
            underworldplayer.custom_update(underworldcamera, gamestate.underworld_map_dict)

            gamestate.update_sprite_dict_and_drawn_map(underworldcamera, underworldplayer.rect.center)

            dagger.update_weapon_position(underworldplayer.rect, underworldplayer.facing_direction, underworldplayer.is_moving_x, underworldplayer.is_moving_y)


            refresh_underworld_draw_order(underworldcamera, underworldplayer)
            #*********************
            underworldcamera.update()
            underworldcamera.custom_draw(underworldplayer)
            
            for enemy in enemy_group:
                if enemy.alive:
                    enemy.custom_update(underworldplayer, underworldcamera)
            
            #Applies lighting to projectile
            for projectile in projectile_group:
                projectile.custom_update(underworldplayer.rect.center)

            enemies_killed = enemy_count - len(enemy_group)

            dagger.update_attack_hitbox_and_detect_collisions(screen, underworldcamera, underworldplayer.rect, underworldplayer.facing_direction, input_events)
            dagger.detect_enemy_weapon_collision(underworldcamera)

            #TEMP *******************************************************************
            underworldcamera.add(enemy_group)
            #print(len(projectile_group))
            underworldcamera.add(coin_group)
            underworldcamera.add(projectile_group)
            underworldcamera.add(coin_drop_text_group)
            for coin in coin_group:
                coin.detect_coin_collision(underworldplayer)
            for projectile in projectile_group:
                projectile.check_player_collision(underworldplayer)

            underworld_hudbar.update_coin_text(underworldplayer.coins_collected)
            #************************************************************************
            #print(f"Enemies remaining: {len(enemy_group)}")

            if not settings.DARKNESS_DEBUG:
                for key in gamestate.underworld_tile_sprite_dict.keys():
                    gamestate.underworld_tile_sprite_dict[key].custom_update(underworldplayer.rect.center)
            
            underworld_hudgroup.draw(screen)
            underworld_hudbar.custom_draw(screen)
            underworld_hudbar.update_health_hud(underworldplayer.health)
            gamestate.selected_world = underworldplayer.gameworld
            
            pygame.display.update()
            clock.tick(60)

        while gamestate.selected_world == "death":
            pygame.mixer.music.stop()
            screen.fill((0, 0, 0))
            pygame.display.update()
            clock.tick(60)

        dungeon_complete = pygame.image.load('assets/splashscreens/dungeonComplete.png').convert_alpha()
        dungeon_complete_rect = dungeon_complete.get_rect()
        dungeon_complete_texts = hud.DungeonCompleteText(underworld_hudbar.coins_earned_in_dungeon, enemies_killed)
        while gamestate.selected_world == "dungeonComplete":
            pygame.mixer.music.stop()
            screen.fill((0, 0, 0))
            dungeon_complete_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)
            screen.blit(dungeon_complete, dungeon_complete_rect.topleft)
            dungeon_complete_texts.custom_draw(screen)
            pygame.display.update()
            input_events = pygame.event.get()
            for event in input_events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        gamestate.selected_world = "overworld"
                        gamestate.overworld_coincount += underworld_hudbar.coins_earned_in_dungeon
            clock.tick(60)

        dungeon_death = pygame.image.load('assets/splashscreens/dungeonDeath.png').convert_alpha()
        dungeon_death_rect = dungeon_death.get_rect()
        while gamestate.selected_world == "dungeonDeath":
            pygame.mixer.music.stop()
            screen.fill((0, 0, 0))
            dungeon_death_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)
            screen.blit(dungeon_death, dungeon_death_rect.topleft)
            pygame.display.update()
            input_events = pygame.event.get()
            for event in input_events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        gamestate.selected_world = "overworld"
            clock.tick(60)            

if __name__ == "__main__":
    main()