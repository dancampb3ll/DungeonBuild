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

TILE_COUNT = settings.SCREEN_HEIGHT / settings.OVERWORLD_TILE_SIZE
DEFAULT_NO_TILE_PORTAL = [None, None, None]

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
            "tinyPot": 0
            }

        self.underworldcamera = CameraGroup()
        self.underworld_map_dict = {}
        self.underworld_npc_spawn_dict = {}
        self.underworld_tile_sprite_dict = {}
        self.underworld_todraw_tile_dict = {}

    def add_inventory_minus_coincount_from_shop_purchases(self, shop_obj):
        result = shop_obj.get_purchased_items_and_cost()
        item = result[0]
        purchased_amount = result[1]
        purchased_cost = result[2]

        self.build_inventory[item] += purchased_amount
        #print("purchased_cost pre ", purchased_cost)
        #print("coins pre ", self.overworld_coincount)
        self.overworld_coincount -= purchased_cost
        #print("purchased_cost post ", purchased_cost)
        #print("coins post ", self.overworld_coincount)
        return

    def temp_spawn_creation_REFACTOR(self):
        #Temporary test for making portal work - makes a dungeon at 20,20
        build_and_perform_tiledict_spritedict_updates(self, "smallDungeon", (20, 20))
        self.overworld_tile_sprite_dict.get((20, 20)).portal_type = "underworld"
        self.overworld_tile_sprite_dict.get((20, 20)).portal_destination = (27, 27)
        self.overworld_tile_sprite_dict.get((20, 20)).portal_collision_side = "bottom"
        self.overworld_tile_sprite_dict.get((21, 20)).portal_type = "underworld"
        self.overworld_tile_sprite_dict.get((21, 20)).portal_destination = (27, 27)
        self.overworld_tile_sprite_dict.get((21, 20)).portal_collision_side = "bottom"
        build_and_perform_tiledict_spritedict_updates(self, "shopHut", (28, 12))

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
        self.overworldplayer_init_grid_x = 30#12
        self.overworldplayer_init_grid_y = 20#32
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

    def reset_initial_gamestate(self):
        self.overworldcamera = CameraGroup()

    def reset_underworld_gamestate(self):
        self.underworld_map_dict.clear()
        self.underworld_npc_spawn_dict.clear()
        self.underworld_tile_sprite_dict.clear()
        self.underworld_todraw_tile_dict.clear()

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
            gamestate.overworld_tile_sprite_dict[(x, y)].kill()
            #Creates an instance of the new tile
            gamestate.overworld_tile_sprite_dict[(x, y)] = overworld.tiles.OutdoorTile(x, y, tilename, gamestate.overworldcamera, DEFAULT_NO_TILE_PORTAL)
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
        return
    x = placementcoord[0]
    y = placementcoord[1]
    tile_sprite = gamestate.overworld_tile_sprite_dict.get((x,y), None)
    if tile_sprite is None:
        return
    if tile_sprite.tile != "overgroundBorder":
        return
    gamestate.overworld_tile_sprite_dict[(x, y)].kill()
    gamestate.overworld_tile_sprite_dict[(x, y)] = overworld.tiles.OutdoorTile(x, y, "overgroundGrass", gamestate.overworldcamera, DEFAULT_NO_TILE_PORTAL)
    draw_new_border_tiles_from_grass_placement(gamestate, x, y)
    gamestate.overworld_map_dict[(int(x), int(y))] = 2
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
    GRASS_SFX = pygame.mixer.Sound("assets/sfx/GrassPlacement.mp3")
    BUILDING_SFX = pygame.mixer.Sound("assets/sfx/BuildingPlacement.mp3")
    gamestate = GameState()
    gamestate.current_music = "assets/music/overworld/Lost-Jungle.mp3"


    mainloop = True
    while mainloop:
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
            clock.tick(60)

        ################################################################################################
        # Pre-overworld initialisation                                                                 #
        ################################################################################################
        
        #Camera must be the first Pygame object defined.
        overworldcamera = gamestate.overworldcamera

        #HUD is separate from the camera
        overworld_hudgroup = pygame.sprite.Group()
        overworld_bottomhud = hud.OverworldBottomHud()
        overworld_cointext = hud.OverworldCoinText(overworld_bottomhud.rect.topleft[0], overworld_bottomhud.rect.topleft[1], gamestate.overworld_coincount)
        buildhud = hud.BuildHud()
        overworld_hudgroup.add(overworld_cointext)

        shopmenu_hud = hud.ShopMenu()


        underworld_hudgroup = pygame.sprite.Group()

        debugtext = hud.DebugText()
        screentext = pygame.sprite.Group()
        screentext.add(debugtext)

        building_tooltips = pygame.sprite.Group()
        tooltip_left = None
        tooltip_right = None
        pygame.mixer.music.play(-1) #Repeat unlimited
        player = OverworldPlayer(overworldcamera, gamestate.overworldplayer_init_grid_x, gamestate.overworldplayer_init_grid_y)
        gamestate.reset_underworld_gamestate()
        while gamestate.selected_world == "overworld":
            #print("len of camera group: ", len(overworldcamera))
            #print(gamestate.overworld_map_dict)
            gamestate.selected_world = player.gameworld
            input_events = pygame.event.get()
            for event in input_events:
                if event.type == pygame.QUIT:
                    mainloop = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        gamestate.toggle_overworld_pause_state()

            if gamestate.in_overworld_pause_menu:
                overworld_pause_menu = hud.OverworldPauseMenu()
                while gamestate.in_overworld_pause_menu:
                    input_events = pygame.event.get()
                    for event in input_events:
                        if event.type == pygame.QUIT:
                            mainloop = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                gamestate.toggle_overworld_pause_state()
                    overworld_pause_menu.custom_draw(screen)
                    if gamestate.in_overworld_pause_menu:
                        gamestate.selected_world, gamestate.in_overworld_pause_menu = overworld_pause_menu.get_gamestate_world_and_pause_status_from_quit_button(input_events)
                    if gamestate.selected_world == "title":
                        pygame.mixer.music.stop()
                        gamestate.save_game_file(player.gridx, player.gridy)
                        title_screen = hud.TitleMenu()
                    pygame.display.update()
                    clock.tick(60)
                overworld_pause_menu.kill()

            if gamestate.current_music != overworld_track:
                pygame.mixer.music.load(overworld_track)
                pygame.mixer.music.play(-1) #Repeat unlimited
            gamestate.update_current_music(overworld_track)
            screen.fill((10, 10, 18))
            
            overworld_cointext.update_coin_count(gamestate.overworld_coincount)

            #Test
            shopkeeper_test_coords = settings.OVERWORLD_SHOPKEEPER_COORDS
            player_in_shop_range = player.get_shop_window_shown_bool(shopkeeper_test_coords)

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

            overworldcamera.custom_draw(player)

            ################################################################################################
            # Overworld HUD
            ################################################################################################
            debugtext.update(player.gridx, player.gridy, gamestate.overworld_map_dict, overworld.tiles.TILE_MAPPINGS)
            screentext.draw(screen)

            tooltip_left, tooltip_right = check_buildmode_and_update_tooltips(player.buildmode, player.selected_building, tooltip_left, tooltip_right, input_events, building_tooltips)

            buildhud.custom_update_and_draw(screen)
            building_tooltips.update()
            building_tooltips.draw(screen)
            buildhud.set_items_from_gamestate_inventory(gamestate.build_inventory)
            overworld_bottomhud.set_current_grass_count(gamestate.build_inventory)
            shopmenu_hud.custom_update_and_draw(player_in_shop_range, screen, input_events, gamestate.overworld_coincount)
            gamestate.add_inventory_minus_coincount_from_shop_purchases(shopmenu_hud)
            overworld_bottomhud.custom_draw(screen)
            overworld_hudgroup.draw(screen)

            pygame.display.update()
            clock.tick(60)
        player.kill()


        ################################################################################################
        # Pre-underworld initialisation                                                                 
        ################################################################################################
        gamestate.underworldcamera = CameraGroup()
        underworldcamera = gamestate.underworldcamera

        gamestate.generate_underworld_dungeon_and_update_map()

        underworld.npc.reset_groups()
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
                    gamestate.selected_world = False


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

        dungeon_complete = pygame.image.load('assets/splashscreens/dungeonComplete.png').convert_alpha()
        dungeon_complete_rect = dungeon_complete.get_rect()
        dungeon_complete_texts = hud.DungeonCompleteText(underworld_hudbar.coins_earned_in_dungeon, enemies_killed)
        while gamestate.selected_world == "dungeonComplete":
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
            clock.tick(60)

        dungeon_death = pygame.image.load('assets/splashscreens/dungeonDeath.png').convert_alpha()
        dungeon_death_rect = dungeon_death.get_rect()
        while gamestate.selected_world == "dungeonDeath":
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
            clock.tick(60)

if __name__ == "__main__":
    main()