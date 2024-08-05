import pygame
import overworld.tiles
import overworld.buildings
import underworld.tiles
import underworld.player
import underworld.npc
import settings
import hud
import math
import os
import json
import copy
from overworld.player import Player as OverworldPlayer
from camera import CameraGroup
import utils
import sys

TILE_COUNT = settings.SCREEN_HEIGHT / settings.OVERWORLD_TILE_SIZE
DEFAULT_NO_TILE_PORTAL = [None, None, None]

OVERWORLD_TRACK = "assets/music/overworld/Lost-Jungle.mp3"
UNDERWORLD_TRACK = "assets/music/underworld/Realm-of-Fantasy.mp3"
FPS = settings.FPS

class GameState():
    def __init__(self):
        self.selected_world = "title"
        self.current_music = None

        self.overworld_map_dict = {}
        self.overworld_tile_sprite_dict = {}
        self.overworldcamera = CameraGroup()
        self.overworldplayer_init_grid_x = 0
        self.overworldplayer_init_grid_y = 0
        self.overworld_coincount = 5
        self.in_overworld_pause_menu = False
        self.save_name = "NaN"

        self.build_inventory = {
            "overgroundGrass": 0,
            "tinyPot": 0,
            "tinyFlower": 0,
            "cobblestone": 0,
            "bench": 0
            }

        self.underworld_camera = CameraGroup()
        self.underworld_map_dict = {}
        self.underworld_npc_spawn_dict = {}
        self.underworld_tile_sprite_dict = {}
        self.underworld_todraw_tile_dict = {}

        #Delta time
        self.dt = None

    def add_inventory_minus_coincount_from_shop_purchases(self, shop_obj):
        result = shop_obj.get_purchased_items_and_cost()
        item = result[0]
        purchased_amount = result[1]
        purchased_cost = result[2]

        self.build_inventory[item] += purchased_amount
        self.overworld_coincount -= purchased_cost
        return

    def temp_spawn_creation_REFACTOR(self):
        #Temporary test for making portal work - makes a dungeon at 20,20
        build_and_perform_tiledict_spritedict_updates(self, "smallDungeon", (20, 20), {"smallDungeon":1})
        self.overworld_tile_sprite_dict.get((20, 20)).portal_type = "underworld"
        self.overworld_tile_sprite_dict.get((20, 20)).portal_destination = (27, 27)
        self.overworld_tile_sprite_dict.get((20, 20)).portal_collision_side = "bottom"
        self.overworld_tile_sprite_dict.get((21, 20)).portal_type = "underworld"
        self.overworld_tile_sprite_dict.get((21, 20)).portal_destination = (27, 27)
        self.overworld_tile_sprite_dict.get((21, 20)).portal_collision_side = "bottom"
        build_and_perform_tiledict_spritedict_updates(self, "shopHut", (28, 12), {"shopHut":1})

    def initialise_tile_sprite_dict_from_tilemap(self):
        self.overworld_tile_sprite_dict.clear()
        #Map initialisation - creates pygame sprites for tiles that aren't blanks (value 0)
        for coord in self.overworld_map_dict.keys():
            x = coord[0]
            y = coord[1]
            tiletype = self.overworld_map_dict[(x, y)]
            if tiletype != 0:
                tilename = overworld.tiles.TILE_MAPPINGS[tiletype]
                self.overworld_tile_sprite_dict[(x, y)] = overworld.tiles.OutdoorTile(x, y, tilename, self.overworldcamera, DEFAULT_NO_TILE_PORTAL)

    def create_new_game_gamestate(self, worldname):
        self.reset_initial_gamestate()
        self.overworld_map_dict = copy.deepcopy(overworld.tiles.default_overworldmapdict)
        self.overworldplayer_init_grid_x = 20
        self.overworldplayer_init_grid_y = 27
        self.initialise_tile_sprite_dict_from_tilemap()
        self.temp_spawn_creation_REFACTOR()
        self.save_name = worldname
        self.selected_world = "overworld"

    def save_game_file(self, playergridx, playergridy):
        def convert_dict_keys_to_str(data):
            """
            Needed to save coordinates of tiles to the save file, as tuples are not valid.
            Works with recusion.
            """
            if isinstance(data, dict):
                return {str(k): convert_dict_keys_to_str(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [convert_dict_keys_to_str(item) for item in data]
            elif isinstance(data, set):
                return {convert_dict_keys_to_str(item) for item in data}
            elif isinstance(data, tuple):
                return tuple(convert_dict_keys_to_str(item) for item in data)
            elif hasattr(data, '__json__'):
                return data.__json__()
            else:
                return data
        
        save_data = {
            "playergridx": playergridx,
            "playergridy": playergridy,
            "overworld_coincount": self.overworld_coincount,
            "overworld_map_dict": convert_dict_keys_to_str(self.overworld_map_dict),
            "overworld_tile_sprite_dict": convert_dict_keys_to_str(self.overworld_tile_sprite_dict),
            "build_inventory": convert_dict_keys_to_str(self.build_inventory)
        }
        
        file_path = f"saves/{self.save_name}.json"
        with open(file_path, 'w') as file:
            json.dump(save_data, file, indent=4)

    def load_game_file(self, save_name):
        self.reset_initial_gamestate()
        with open(f"saves/{save_name}.json", "r") as file:
            save = json.load(file)

        self.save_name = save_name

        self.overworldplayer_init_grid_x = save["playergridx"]
        self.overworldplayer_init_grid_y = save["playergridy"]
        self.overworld_coincount = save["overworld_coincount"]
        try:
            self.build_inventory = save["build_inventory"]
        except:
            pass # Use default empty build inventory if cannot load (old save file, etc)

        #Manipulating tiles in JSON string format back to tuple key format
        raw_save_overworld_map_dict = save["overworld_map_dict"]
        
        
        overworld_map_dict = {}
        for key_str, value in raw_save_overworld_map_dict.items():
            # Convert string key to tuple
            key_tuple = tuple(map(int, key_str.strip('()').split(', ')))
        
            # Add to the converted dictionary
            overworld_map_dict[key_tuple] = value

        self.overworld_map_dict = overworld_map_dict

        self.initialise_tile_sprite_dict_from_tilemap()
        
        self.temp_spawn_creation_REFACTOR()
        self.selected_world = "overworld"

    def toggle_overworld_pause_state(self):
        if self.in_overworld_pause_menu:
            self.in_overworld_pause_menu = False
        else:
            self.in_overworld_pause_menu = True

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
        def determine_to_draw_dict(self, camera_group, player_center):
            player_gridx = player_center[0] // settings.UNDERWORLD_TILE_SIZE
            player_gridy = player_center[1] // settings.UNDERWORLD_TILE_SIZE
            self.underworld_todraw_tile_dict = {}
            for coord in map.keys():
                gridx = coord[0]
                gridy = coord[1]
                distance = utils.calculate_distance_pythagoras((gridx, gridy), (player_gridx, player_gridy))
                if distance < settings.UNDERWORLD_DRAW_DISTANCE:
                    self.underworld_todraw_tile_dict[(gridx, gridy)] = True

        determine_to_draw_dict(self, camera_group, player_center)

        for coord in map.keys():
            gridx = coord[0]
            gridy = coord[1]
            material = map[coord][0]
            portal = map[coord][1]
            #Handling tiles to draw not in current sprite dict
            if self.underworld_todraw_tile_dict.get(coord, False) == True:
                if self.underworld_tile_sprite_dict.get(coord, False) == False:
                    self.underworld_tile_sprite_dict[(gridx, gridy)] = underworld.tiles.UnderworldTile(gridx, gridy, material, camera_group, portal, player_center)
            else:
                if self.underworld_tile_sprite_dict.get(coord, False) != False:
                    self.underworld_tile_sprite_dict[(gridx, gridy)].kill()
                    del self.underworld_tile_sprite_dict[(gridx, gridy)]

    def reset_initial_gamestate(self):
        self.overworldcamera = CameraGroup()

    def reset_underworld_gamestate(self):
        self.underworld_map_dict.clear()
        self.underworld_npc_spawn_dict.clear()
        self.underworld_tile_sprite_dict.clear()
        self.underworld_todraw_tile_dict.clear()

def build_and_perform_tiledict_spritedict_updates(gamestate, structuretype, topleftplacementcoord: tuple, build_inventory, player_coords_list_to_avoid_building_on=[None], play_sfx = False):
        """Gets the world map, looks where the structure is to be built, and if possible deletes sprites from the spritedict.
        Returns the new world map dict with new buildings as replacements for old.
        """
        if topleftplacementcoord is None:
            return

        if build_inventory.get(structuretype, None) is None:
            return
        
        if build_inventory[structuretype] <= 0:
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
            gamestate.overworld_tile_sprite_dict[(x, y)].kill()
            #Creates an instance of the new tile
            gamestate.overworld_tile_sprite_dict[(x, y)] = overworld.tiles.OutdoorTile(x, y, tilename, gamestate.overworldcamera, DEFAULT_NO_TILE_PORTAL)
        
        build_inventory[structuretype] -= 1
        if play_sfx:
            play_sfx.play()
        return

def draw_new_border_tiles_from_grass_placement(gamestate, placementx, placementy):
    for adjacentoffset in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
        checkx = placementx + adjacentoffset[0]
        checky = placementy + adjacentoffset[1]

        check_sprite = gamestate.overworld_tile_sprite_dict.get((checkx, checky), None)
        if check_sprite is None:
            gamestate.overworld_tile_sprite_dict[(checkx, checky)] = overworld.tiles.OutdoorTile(checkx, checky, "overgroundBorder", gamestate.overworldcamera, DEFAULT_NO_TILE_PORTAL)
            gamestate.overworld_map_dict[(checkx, checky)] = 4

def build_grass_block_and_perform_tile_sprite_updates(gamestate, placementcoord, play_sfx = None):
    if placementcoord is None:
        return 0
    x = placementcoord[0]
    y = placementcoord[1]
    tile_sprite = gamestate.overworld_tile_sprite_dict.get((x,y), None)
    if tile_sprite is None:
        return 0
    if tile_sprite.tile != "overgroundBorder":
        return 0
    gamestate.overworld_tile_sprite_dict[(x, y)].kill()
    gamestate.overworld_tile_sprite_dict[(x, y)] = overworld.tiles.OutdoorTile(x, y, "overgroundGrass", gamestate.overworldcamera, DEFAULT_NO_TILE_PORTAL)
    draw_new_border_tiles_from_grass_placement(gamestate, x, y)
    gamestate.overworld_map_dict[(int(x), int(y))] = 2
    if play_sfx:
        play_sfx.play()
    return 1

def refresh_underworld_draw_order(camera_group, player):
    #Drawn from lowest priority to max
    if player.facing_direction == "down":
        draw_order = ["tile", "npc", "player", "weapon", "coin", "projectile", "floatingText"]
    else:
        draw_order = ["tile", "npc", "weapon", "player", "coin", "projectile", "floatingText"]

    for sprite_type in draw_order:
        for sprite in camera_group.sprites():
            if sprite.type == sprite_type:    
                camera_group.remove(sprite)
                camera_group.add(sprite)

def initialise_game():
    pygame.init()
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), vsync=1)
    clock = pygame.time.Clock()
    pygame.display.set_caption('DungeonBuild')
    pygame.mixer.init()
    pygame.mixer.music.load(OVERWORLD_TRACK)
    gamestate = GameState()
    gamestate.current_music = OVERWORLD_TRACK
    sfx_bank = {
        "GRASS_SFX": pygame.mixer.Sound("assets/sfx/GrassPlacement.mp3"),
        "BUILDING_SFX": pygame.mixer.Sound("assets/sfx/BuildingPlacement.mp3")
    }
    floating_text_group = utils.floating_text_group #Creates plain text that floats upwards in any gameworld. 
    return screen, clock, gamestate, sfx_bank, floating_text_group

def update_title_menu(screen, clock, gamestate):
    title_screen = hud.TitleMenu()
    while gamestate.selected_world == "title":
        input_events = pygame.event.get()
        screen.fill((0, 0, 0))
        title_screen.custom_draw(screen, input_events)
        title_screen_state = title_screen.get_newgame_or_loadgame_or_loadgameselection_clicked(input_events)
        if title_screen_state == "loadgamefile":
            selected_world = title_screen.get_selected_world_name()
            if selected_world != "":
                gamestate.load_game_file(selected_world)
        elif title_screen_state == "newgamecreated":
            gamestate.create_new_game_gamestate(title_screen.worldname_text_entered)
        pygame.display.update()
        gamestate.dt = clock.tick(FPS) / 1000

def initialise_overworld(gamestate):
    pygame.mixer.music.play(-1) #Repeat unlimited
    overworld_camera = gamestate.overworldcamera
    overworld_hudgroup = pygame.sprite.Group()
    overworld_bottomhud = hud.OverworldBottomHud()
    overworld_cointext = hud.OverworldCoinText(overworld_bottomhud.rect.topleft[0], overworld_bottomhud.rect.topleft[1], gamestate.overworld_coincount)
    buildhud = hud.BuildHud()
    overworld_hudgroup.add(overworld_cointext)
    shopmenu_hud = hud.ShopMenu()
    debugtext = hud.DebugText()
    debugtext_group = pygame.sprite.Group()
    debugtext_group.add(debugtext)
    overworld_player = OverworldPlayer(overworld_camera, gamestate.overworldplayer_init_grid_x, gamestate.overworldplayer_init_grid_y)
    return overworld_player, overworld_camera, buildhud, overworld_cointext, debugtext, debugtext_group, overworld_bottomhud, shopmenu_hud, overworld_hudgroup

def update_pause_menu(screen, clock, gamestate, overworld_player):
    overworld_pause_menu = hud.OverworldPauseMenu()
    while gamestate.in_overworld_pause_menu:
        input_events = pygame.event.get()
        for event in input_events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    gamestate.toggle_overworld_pause_state()
        overworld_pause_menu.custom_draw(screen)
        if gamestate.in_overworld_pause_menu:
            gamestate.selected_world, gamestate.in_overworld_pause_menu = overworld_pause_menu.get_gamestate_world_and_pause_status_from_quit_button(input_events)
        if gamestate.selected_world == "title":
            pygame.mixer.music.stop()
            gamestate.save_game_file(overworld_player.gridx, overworld_player.gridy)
        pygame.display.update()
        gamestate.dt = clock.tick(FPS) / 1000
    overworld_pause_menu.kill()

def update_overworld(screen, clock, gamestate, overworld_player, overworld_camera, buildhud, overworld_cointext,
                      overworld_bottomhud, overworld_hudgroup, shopmenu_hud, floating_text_group, debugtext, debugtext_group, sfx_bank):
    gamestate.selected_world = overworld_player.gameworld
    
    input_events = pygame.event.get()
    for event in input_events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                gamestate.toggle_overworld_pause_state()

    if gamestate.in_overworld_pause_menu:
        update_pause_menu(screen, clock, gamestate, overworld_player)
        

    if gamestate.current_music != OVERWORLD_TRACK:
        pygame.mixer.music.load(OVERWORLD_TRACK)
        pygame.mixer.music.play(-1) #Repeat unlimited
    gamestate.update_current_music(OVERWORLD_TRACK)
    screen.fill((10, 10, 18))
    
    overworld_cointext.update_coin_count(gamestate.overworld_coincount)

    #Test
    shopkeeper_test_coords = settings.OVERWORLD_SHOPKEEPER_COORDS
    player_in_shop_range = overworld_player.get_shop_window_shown_bool(shopkeeper_test_coords)

    #overworldcamera contains tile sprites, which are used to detect collisions.
    overworld_player.move_player(overworld_camera, gamestate.dt)
    overworld_player.set_build_mode_from_input(input_events, buildhud, overworld_camera)
    overworld_player.custom_update()

    #If none returned from get coords, nothing is changed on overworldmap dict
    player_building_placement_coords_topleft = overworld_player.place_building_get_coords(input_events, overworld_camera)
    player_corner_coords_list = overworld_player.get_player_corner_grid_locations()
    build_and_perform_tiledict_spritedict_updates(gamestate, buildhud.selected_build_item, player_building_placement_coords_topleft, gamestate.build_inventory, player_corner_coords_list, sfx_bank["BUILDING_SFX"])

    #If none returned from get coords, nothing is changed on overworldmap dict
    player_Grass_placement_coords = overworld_player.place_grass_block_get_coords(input_events, overworld_camera, gamestate.build_inventory)
    valid_grass_build = build_grass_block_and_perform_tile_sprite_updates(gamestate, player_Grass_placement_coords, sfx_bank["GRASS_SFX"])
    if valid_grass_build == 1:
        gamestate.build_inventory["overgroundGrass"] -= 1

    overworld_camera.update()
    overworld_camera.custom_draw(overworld_player)
    

    ################################################################################################
    # Overworld HUD
    ################################################################################################
    debugtext.update(overworld_player.gridx, overworld_player.gridy, gamestate.overworld_map_dict, overworld.tiles.TILE_MAPPINGS)
    debugtext_group.draw(screen)

    buildhud.custom_update_and_draw(screen)
    buildhud.set_items_from_gamestate_inventory(gamestate.build_inventory, input_events)
    overworld_bottomhud.set_current_grass_count(gamestate.build_inventory)
    shopmenu_hud.custom_update_and_draw(player_in_shop_range, screen, input_events, gamestate.overworld_coincount, overworld_player.buildmode, overworld_camera.offset)
    gamestate.add_inventory_minus_coincount_from_shop_purchases(shopmenu_hud)
    overworld_bottomhud.custom_draw(screen)
    overworld_hudgroup.draw(screen)
    overworld_camera.add(floating_text_group)

    pygame.display.update()
    gamestate.dt = clock.tick(FPS) / 1000

def initialise_underworld(gamestate, overworld_player):
    overworld_player.kill()
    underworld_hudgroup = pygame.sprite.Group()
    gamestate.reset_underworld_gamestate()
    gamestate.underworld_camera = CameraGroup()
    underworld_camera = gamestate.underworld_camera

    gamestate.generate_underworld_dungeon_and_update_map()

    underworld.npc.reset_groups()
    enemy_group = underworld.npc.enemy_group
    coin_group = underworld.npc.coin_group
    projectile_group = underworld.npc.projectile_group

    gamestate.spawn_enemies_from_spawn_dict(enemy_group)
    dagger = underworld.player.Weapon(underworld_camera, "dagger")
    underworld_player = underworld.player.Player(underworld_camera)
    underworld_hudbar = hud.UnderworldHud()
    underworld_hudgroup.add(underworld_hudbar)

    enemy_count = len(enemy_group)
    enemies_killed = 0
    return underworld_camera, underworld_player, dagger, enemy_group, projectile_group, enemy_count, coin_group, underworld_hudbar, underworld_hudgroup, enemies_killed

def update_underworld(screen, clock, gamestate, underworld_camera, underworld_player, dagger, enemy_group, projectile_group, enemy_count,
                    coin_group, floating_text_group, underworld_hudbar, underworld_hudgroup):
    input_events = pygame.event.get()
    for event in input_events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            


    if gamestate.current_music != UNDERWORLD_TRACK:
        pygame.mixer.music.load(UNDERWORLD_TRACK)
        pygame.mixer.music.play(-1) #Repeat unlimited
    gamestate.update_current_music(UNDERWORLD_TRACK)
    screen.fill((0, 0, 0))

    underworld_player.move_player(underworld_camera, gamestate.underworld_map_dict, gamestate.dt)
    underworld_player.custom_update(underworld_camera, gamestate.underworld_map_dict, gamestate.dt)

    gamestate.update_sprite_dict_and_drawn_map(underworld_camera, underworld_player.rect.center)

    dagger.update_weapon_position(underworld_player.rect, underworld_player.facing_direction, underworld_player.is_moving_x, underworld_player.is_moving_y)


    refresh_underworld_draw_order(underworld_camera, underworld_player)
    #*********************
    underworld_camera.update()
    underworld_camera.custom_draw(underworld_player)
    
    for enemy in enemy_group:
        if enemy.alive:
            enemy.custom_update(underworld_player, underworld_camera, gamestate.dt)
    
    #Applies lighting to projectile
    for projectile in projectile_group:
        projectile.custom_update(underworld_player.rect.center, gamestate.dt)

    enemies_killed = enemy_count - len(enemy_group)

    dagger.update_attack_hitbox_and_detect_collisions(screen, underworld_camera, underworld_player.rect, underworld_player.facing_direction, input_events)
    dagger.detect_enemy_weapon_collision(underworld_camera)

    #TEMP *******************************************************************
    underworld_camera.add(enemy_group)
    underworld_camera.add(coin_group)
    underworld_camera.add(projectile_group)
    underworld_camera.add(floating_text_group)
    for coin in coin_group:
        coin.detect_coin_collision(underworld_player)
    for projectile in projectile_group:
        projectile.check_player_collision(underworld_player)

    underworld_hudbar.update_coin_text(underworld_player.coins_collected)
    #************************************************************************

    if not settings.DARKNESS_DEBUG:
        for key in gamestate.underworld_tile_sprite_dict.keys():
            gamestate.underworld_tile_sprite_dict[key].custom_update(underworld_player.rect.center)
    
    underworld_hudgroup.draw(screen)
    underworld_hudbar.custom_draw(screen)
    underworld_hudbar.update_health_hud(underworld_player.health)
    gamestate.selected_world = underworld_player.gameworld
    
    pygame.display.update()
    gamestate.dt = clock.tick(FPS) / 1000

def initialise_dungeon_complete_screen(underworld_hudbar, enemies_killed):
        dungeon_complete = pygame.image.load('assets/splashscreens/dungeonComplete.png').convert_alpha()
        dungeon_complete_rect = dungeon_complete.get_rect()
        dungeon_complete_texts = hud.DungeonCompleteText(underworld_hudbar.coins_earned_in_dungeon, enemies_killed)
        return dungeon_complete, dungeon_complete_rect, dungeon_complete_texts

def update_dungeon_complete(clock, screen, gamestate, dungeon_complete, dungeon_complete_rect, dungeon_complete_texts, underworld_hudbar):
    pygame.mixer.music.stop()
    screen.fill((0, 0, 0))
    dungeon_complete_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)
    screen.blit(dungeon_complete, dungeon_complete_rect.topleft)
    dungeon_complete_texts.custom_draw(screen)
    
    input_events = pygame.event.get()
    for event in input_events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                gamestate.selected_world = "overworld"
                gamestate.overworld_coincount += underworld_hudbar.coins_earned_in_dungeon
    pygame.display.update()
    gamestate.dt = clock.tick(FPS) / 1000

def initialise_dungeon_death_screen():
    dungeon_death = pygame.image.load('assets/splashscreens/dungeonDeath.png').convert_alpha()
    dungeon_death_rect = dungeon_death.get_rect()
    return dungeon_death, dungeon_death_rect

def update_dungeon_death_screen(clock, screen, gamestate, dungeon_death, dungeon_death_rect):
    pygame.mixer.music.stop()
    screen.fill((0, 0, 0))
    dungeon_death_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)
    screen.blit(dungeon_death, dungeon_death_rect.topleft)
    input_events = pygame.event.get()
    for event in input_events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                gamestate.selected_world = "overworld"
    pygame.display.update()
    gamestate.dt = clock.tick(FPS) / 1000

def main():
    screen, clock, gamestate, sfx_bank, floating_text_group = initialise_game()
    while True:
        #Title
        update_title_menu(screen, clock, gamestate)

        #Overworld
        (overworld_player, overworld_camera, buildhud, overworld_cointext, debugtext, debugtext_group,
        overworld_bottomhud, shopmenu_hud, overworld_hudgroup) = initialise_overworld(gamestate)
        while gamestate.selected_world == "overworld":
            update_overworld(screen, clock, gamestate, overworld_player, overworld_camera, buildhud, overworld_cointext,
                            overworld_bottomhud, overworld_hudgroup, shopmenu_hud, floating_text_group, debugtext, debugtext_group, sfx_bank)

        #Underworld
        (underworld_camera, underworld_player, dagger, enemy_group, projectile_group,
        enemy_count, coin_group, underworld_hudbar, underworld_hudgroup, enemies_killed) = initialise_underworld(gamestate, overworld_player)
        while gamestate.selected_world == "underworld":
            update_underworld(screen, clock, gamestate, underworld_camera, underworld_player, dagger, enemy_group, projectile_group, enemy_count,
                    coin_group, floating_text_group, underworld_hudbar, underworld_hudgroup)

        #Dungeon Complete
        dungeon_complete, dungeon_complete_rect, dungeon_complete_texts = initialise_dungeon_complete_screen(underworld_hudbar, enemies_killed)
        while gamestate.selected_world == "dungeonComplete":
            update_dungeon_complete(clock, screen, gamestate, dungeon_complete, dungeon_complete_rect, dungeon_complete_texts, underworld_hudbar)

        #Dungeon Death
        dungeon_death, dungeon_death_rect = initialise_dungeon_death_screen()
        while gamestate.selected_world == "dungeonDeath":
            update_dungeon_death_screen(clock, screen, gamestate, dungeon_death, dungeon_death_rect)

if __name__ == "__main__":
    main()