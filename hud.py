import pygame
import settings
import os
import json


class DebugText(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.font_size = 12
        self.font = pygame.font.SysFont("Courier New", self.font_size)
        
        self.font_colour = (255, 255, 255)
    

    def update(self, playergridx, playergridy, mapdict, tiledict):
        self.playergridx = playergridx
        self.playergridy = playergridy
        self.tile = mapdict.get((playergridx, playergridy), "error")
        self.material = tiledict.get(self.tile, "Invalid Tile")
        self.text = f"Player x on grid: {self.playergridx} | Player y on grid: {self.playergridy} | Map material at x,y: {self.material}"
        self.image = self.font.render(self.text, True, self.font_colour)
        self.rect = self.image.get_rect(topleft = (5, 5))

class OverworldBottomHud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = "hud"
        self.image = pygame.image.load("assets/hud/hudbar.png").convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.x = settings.SCREEN_WIDTH - self.rect.w
        self.rect.y = settings.SCREEN_HEIGHT - self.rect.h
        
        self.grass_count = 0
        self.grass_count_font_size = 16
        self.grass_count_font = pygame.font.SysFont("Courier New", self.grass_count_font_size, bold=True)
        self.grass_count_font_colour = (0, 0, 0)
        self.grass_count_text_image = self.grass_count_font.render(str(self.grass_count), True, self.grass_count_font_colour)
        self.grass_count_text_x = self.rect.x + 75
        self.grass_count_text_y = self.rect.y + 7

    def set_current_grass_count(self, player_inv):
        self.grass_count = player_inv["overgroundGrass"]
        self.grass_count_text_image = self.grass_count_font.render(str(self.grass_count), True, self.grass_count_font_colour)

    def custom_draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
        screen.blit(self.grass_count_text_image, (self.grass_count_text_x, self.grass_count_text_y))
        
class BuildHud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.bar_image = pygame.image.load("assets/hud/buildhudbar.png").convert_alpha()
        self.bar_rect = self.bar_image.get_rect()
        self.bar_rect.x = settings.SCREEN_WIDTH - self.bar_rect.w
        self.bar_rect.y = 100
        self.player_in_buildmode = False

        self.player_inventory = {}
        
        self.MAX_THUMBNAIL_SIZE = 50
        self.MAX_BUILDINGS_PER_BAR = 6
        self.SPACE_BETWEEN_BUILDING_THUMBNAILS = (self.bar_rect.height - self.MAX_BUILDINGS_PER_BAR * self.MAX_THUMBNAIL_SIZE) // (self.MAX_BUILDINGS_PER_BAR + 1)

        self.buildings = {
            "tinyPot": {
                "item": "tinyPot",
                "imageLink": "assets/hud/buildThumbnails/tinyPot.png",
                "inventory_quantity": None,
            },
            "tinyFlower": {
                "item": "tinyFlower",
                "imageLink": "assets/hud/buildThumbnails/tinyFlower.png",
                "inventory_quantity": None
            },
            "cobblestone": {
                "item": "cobblestone",
                "imageLink": "assets/hud/buildThumbnails/cobblestone.png",
                "inventory_quantity": None
            },
            "bench": {
                "item": "bench",
                "imageLink": "assets/hud/buildThumbnails/bench.png",
                "inventory_quantity": None
            }
        }

        for key in self.buildings.keys():
            self.buildings[key]["image"] = pygame.image.load(self.buildings[key]["imageLink"]).convert_alpha()
            self.buildings[key]["rect"] = self.buildings[key]["image"].get_rect()
            self.buildings[key]["rect"].x = self.bar_rect.centerx - self.buildings[key]["rect"].width // 2

        self.grass_tooltip = pygame.image.load("assets/tooltips/overgroundGrass.png").convert_alpha()
        self.grass_tooltip_rect = self.grass_tooltip.get_rect()
        self.TOOLTIPS_X_OFFSET_FROM_MOUSE = 16
        self.TOOLTIPS_Y_OFFSET_FROM_MOUSE = 16

        self.selected_build_item_index = 0
        self.selected_build_item = None
        self.build_tooltip = pygame.image.load("assets/tooltips/tinyPot.png").convert_alpha()
        self.build_tooltip_rect = self.build_tooltip.get_rect()

        self.quantity_font_size = 11
        self.quantity_font = pygame.font.SysFont("Courier New", self.quantity_font_size, bold=True)
        self.quantity_font_yoffset = 8
        self.quantity_font_colour = (0, 0, 0)

        self.item_background_highlight = pygame.image.load("assets/hud/buildThumbnails/SELECTED.png").convert_alpha()
        self.item_background_highlight_rect = self.item_background_highlight.get_rect()

    def _draw_right_tooltip(self, screen, mouse_pos):
        if mouse_pos[0] < 0 or mouse_pos[0] >= settings.SCREEN_WIDTH:
            return
        if mouse_pos[1] < 0 or mouse_pos[1] >= settings.SCREEN_HEIGHT:
            return
        self.grass_tooltip_rect.x = mouse_pos[0] + self.TOOLTIPS_X_OFFSET_FROM_MOUSE
        self.grass_tooltip_rect.y = mouse_pos[1] + self.TOOLTIPS_Y_OFFSET_FROM_MOUSE
        screen.blit(self.grass_tooltip, self.grass_tooltip_rect.topleft)

    def _draw_left_tooltip(self, screen, mouse_pos):
        if mouse_pos[0] < 0 or mouse_pos[0] >= settings.SCREEN_WIDTH:
            return
        if mouse_pos[1] < 0 or mouse_pos[1] >= settings.SCREEN_HEIGHT:
            return
        if self.selected_build_item is None:
            return
        if self.buildings[self.selected_build_item]["inventory_quantity"] is None:
            return
        self.build_tooltip = pygame.image.load(f"assets/tooltips/{self.selected_build_item}.png").convert_alpha()
        self.build_tooltip_rect = self.build_tooltip.get_rect()
        self.build_tooltip_rect.x = mouse_pos[0] - self.TOOLTIPS_X_OFFSET_FROM_MOUSE
        self.build_tooltip_rect.y = mouse_pos[1] + self.TOOLTIPS_Y_OFFSET_FROM_MOUSE
        screen.blit(self.build_tooltip, self.build_tooltip_rect.topleft)

    def _draw_quantity_text_next_to_items(self, screen):
        if len(self.buildings.keys()) == 0:
            return
        for key in self.buildings.keys():
            if self.buildings[key]["inventory_quantity"] is not None:
                text = self.buildings[key]["inventory_quantity"]
                item_rect = self.buildings[key]["rect"]
                font_image = self.quantity_font.render(str(text), True, self.quantity_font_colour)
                font_image_rect = font_image.get_rect()
                font_image_rect.x = item_rect.centerx - font_image_rect.width // 2
                font_image_rect.y = item_rect.bottom + self.quantity_font_yoffset
                screen.blit(font_image, font_image_rect.topleft)

    def _determine_left_item_held(self):
        items = self._convert_gamestate_inv_to_buildingcount_list_and_set_quantities()
        
        #Below condition ensures the index isn't out of range if an item runs out
        if len(items) == 0 or self.selected_build_item_index > len(items) - 1:
            self.selected_build_item_index = 0
            return
        self.selected_build_item = items[self.selected_build_item_index][0]

    def _draw_build_tooltips(self, screen):
        pos = pygame.mouse.get_pos()
        self._draw_right_tooltip(screen, pos)
        self._draw_left_tooltip(screen, pos)

    def _draw_all_buildings_held_in_inventory(self, screen):
        for key in self.buildings.keys():
            if self.buildings[key]["inventory_quantity"] is not None:
                screen.blit(self.buildings[key]["image"], self.buildings[key]["rect"].topleft)

    def _convert_gamestate_inv_to_buildingcount_list_and_set_quantities(self):
        items = []
        for key, value in self.player_inventory.items():
            if key != "overgroundGrass": #overgroundGrass is a secondary and not shown in the buildings tab as it is on the main GUI
                if value > 0:
                    self.buildings[key]["inventory_quantity"] = value
                    items.append([key, value])
                else:
                    self.buildings[key]["inventory_quantity"] = None
        return items

    def _draw_selected_item_highlight(self, screen):
        if self.selected_build_item is None:
            return
        if self.buildings[self.selected_build_item]["inventory_quantity"] is None:
            return
        self.item_background_highlight_rect.x = self.bar_rect.centerx - self.item_background_highlight_rect.width // 2
        self.item_background_highlight_rect.y = (self.bar_rect.y + #Start
            self.SPACE_BETWEEN_BUILDING_THUMBNAILS + (self.MAX_THUMBNAIL_SIZE + self.SPACE_BETWEEN_BUILDING_THUMBNAILS) * self.selected_build_item_index + #Row number offset
            self.MAX_THUMBNAIL_SIZE // 2 - self.item_background_highlight_rect.height // 2) #Centering
        screen.blit(self.item_background_highlight, self.item_background_highlight_rect.topleft)

    def set_items_from_gamestate_inventory(self, gamestate_inv, input_events):
        self.player_inventory = gamestate_inv
        items = self._convert_gamestate_inv_to_buildingcount_list_and_set_quantities()
        self._scroll_change_build_index(input_events, items)
        self._determine_left_item_held()

    def _refresh_quantity_counts(self):
        count = 0
        for key in self.buildings.keys():
            if self.buildings[key]["inventory_quantity"] is not None:
                self.buildings[key]["count"] = count
                self.buildings[key]["rect"].y = (self.bar_rect.y + #Start
                                self.SPACE_BETWEEN_BUILDING_THUMBNAILS + (self.MAX_THUMBNAIL_SIZE + self.SPACE_BETWEEN_BUILDING_THUMBNAILS) * count + #Row number offset
                                self.MAX_THUMBNAIL_SIZE // 2 - self.buildings[key]["rect"].height // 2) #Centering
                count += 1

    def _scroll_change_build_index(self, input_events, items):
        UPWARD_SCROLL = 1
        DOWNWARD_SCROLL = -1
        for event in input_events:
             if event.type == pygame.MOUSEWHEEL:
                if event.y == DOWNWARD_SCROLL:
                    #Wraparound
                    if self.selected_build_item_index == len(items) - 1 or len(items) == 0:
                        self.selected_build_item_index = 0
                    else:
                        self.selected_build_item_index += 1
                    return
                elif event.y == UPWARD_SCROLL:
                    #Wraparound
                    if self.selected_build_item_index == 0:
                        self.selected_build_item_index = max(len(items) - 1, 0)
                    else:
                        self.selected_build_item_index -= 1
                    return

    def custom_update_and_draw(self, screen):
        if not self.player_in_buildmode:
            return
        screen.blit(self.bar_image, self.bar_rect.topleft)
        self._draw_build_tooltips(screen)
        self._refresh_quantity_counts()
        self._draw_selected_item_highlight(screen)
        self._draw_quantity_text_next_to_items(screen)
        self._draw_all_buildings_held_in_inventory(screen)

class OverworldCoinText(pygame.sprite.Sprite):
    def __init__(self, hudx, hudy, coincount):
        super().__init__()
        self.font_size = 16
        self.font = pygame.font.SysFont("Courier New", self.font_size, bold="True")
        self.font_colour = (0, 0, 0)
        self.hudx = hudx
        self.hudy = hudy
        self.hud_xoffset = 150
        self.hud_yoffset = 7
        self.coincount = coincount
        self.update_coin_display()

    def format_cointext(self, n):
        if n == 0:
            return "0"
        elif n < 100000:
            return f"{n:,}"
        elif n < 10000000:
            return f"{n // 1000}k"
        else:
            return f"{n // 1000000}.{(n % 1000000) // 100000}m"

    def update_coin_display(self):
        self.text = self.format_cointext((self.coincount))
        self.image = self.font.render(self.text, True, self.font_colour)
        self.rect = self.image.get_rect(topleft = (self.hudx + self.hud_xoffset, self.hudy + self.hud_yoffset))

    def update_coin_count(self, newcoincount):
        self.coincount = newcoincount
        self.update_coin_display()

class UnderworldHud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = "hud"
        self.hud = "underworldhud"
        self.image = pygame.image.load("assets/hud/underworld_hudbar.png").convert()
        self.image.set_colorkey((255,0,255))
        self.rect = self.image.get_rect()
        self.rect.x = settings.SCREEN_WIDTH // 2 - self.rect.w // 2
        self.rect.y = settings.SCREEN_HEIGHT - self.rect.h + 3
        self.health = 100
        self.coins_earned_in_dungeon = 0

        #Defining Healthbars
        self.GREEN_HEALTHBAR_START_PIXELX = self.rect.x + 8
        self.GREEN_HEALTHBAR_START_PIXELY = self.rect.y + 6
        self.GREEN_HEALTHBAR_WIDTH = 210
        self.GREEN_HEALTHBAR_HEIGHT = 12
        self.healthrect_green = pygame.Rect(self.GREEN_HEALTHBAR_START_PIXELX, self.GREEN_HEALTHBAR_START_PIXELY, self.GREEN_HEALTHBAR_WIDTH, self.GREEN_HEALTHBAR_HEIGHT)
        
        self.RED_HEALTHBAR_END_PIXELX = self.GREEN_HEALTHBAR_START_PIXELX + self.GREEN_HEALTHBAR_WIDTH + 1
        self.RED_HEALTHBAR_START_PIXELY = self.GREEN_HEALTHBAR_START_PIXELY
        self.red_healthbar_start_pixelx = self.RED_HEALTHBAR_END_PIXELX
        self.RED_HEALTHBAR_HEIGHT = self.GREEN_HEALTHBAR_HEIGHT
        self.RED_HEALTHBAR_WIDTH = 0
        self.healthrect_red = pygame.Rect(self.red_healthbar_start_pixelx, self.RED_HEALTHBAR_START_PIXELY, self.RED_HEALTHBAR_WIDTH, self.RED_HEALTHBAR_HEIGHT)

        #Defining health_text
        self.HEALTH_FONT_SIZE = 16
        self.HEALTH_TEXT_COLOUR = (30, 30, 30)
        self.font_health = pygame.font.SysFont("Courier New", self.HEALTH_FONT_SIZE, bold=True)
        self.HEALTH_POSX = settings.SCREEN_WIDTH // 2 - 14
        self.HEALTH_POSY = settings.SCREEN_HEIGHT - 34
        self.health_text = self.font_health.render(str(self.health), True, self.HEALTH_TEXT_COLOUR)

        #Defining coincount
        self.COIN_FONT_SIZE = 17
        self.COIN_POSX = settings.SCREEN_WIDTH // 2 - 90
        self.COIN_POSY = settings.SCREEN_HEIGHT - 14
        self.font_coin = pygame.font.SysFont("OpenSans-Bold.ttf", self.COIN_FONT_SIZE, bold=False)
        self.COIN_TEXT_COLOUR = (255, 255, 255)
        self.coin_text = self.font_coin.render(str(self.coins_earned_in_dungeon), True, self.COIN_TEXT_COLOUR)


    def update_health_hud(self, health):
        self.health = health
        self.update_red_healthbar()
        self.update_health_text()

    def update_health_text(self):
        self.health_text = self.font_health.render(str(self.health), True, self.HEALTH_TEXT_COLOUR)

    def update_red_healthbar(self):
        percentage_health_taken = (1 - self.health/100)
        total_healthbar_width = self.GREEN_HEALTHBAR_WIDTH
        self.RED_HEALTHBAR_WIDTH = percentage_health_taken * total_healthbar_width
        self.red_healthbar_start_pixelx = self.RED_HEALTHBAR_END_PIXELX - self.RED_HEALTHBAR_WIDTH
        self.healthrect_red = pygame.Rect(self.red_healthbar_start_pixelx, self.RED_HEALTHBAR_START_PIXELY, self.RED_HEALTHBAR_WIDTH, self.RED_HEALTHBAR_HEIGHT)

    def update_coin_text(self, current_coins):
        self.coins_earned_in_dungeon = current_coins
        self.coin_text = self.font_coin.render(str(self.coins_earned_in_dungeon), True, self.COIN_TEXT_COLOUR)
    

    def custom_draw(self, screen):
        #Healthbars
        pygame.draw.rect(screen, (100, 255, 100), self.healthrect_green, 0)
        pygame.draw.rect(screen, (255, 100, 100), self.healthrect_red, 0)

        #Health Text
        screen.blit(self.health_text, (self.HEALTH_POSX, self.HEALTH_POSY))

        #Coin text
        screen.blit(self.coin_text, (self.COIN_POSX, self.COIN_POSY))

class DungeonCompleteText(pygame.sprite.Sprite):
        def __init__(self, coins_earned, monsters_killed):
            super().__init__()
            self.type = "dungeonCompleteText"
            self.coins_earned_in_dungeon = coins_earned
            self.monsters_killed_in_dungeon = monsters_killed

            #Defining coins earnt count
            self.COIN_FONT_SIZE = 17
            self.COIN_POSX = settings.SCREEN_WIDTH // 2 - 190
            self.COIN_POSY = settings.SCREEN_HEIGHT // 2 + 10
            self.font_coin = pygame.font.SysFont("Courier New", self.COIN_FONT_SIZE, bold=True)
            self.COIN_TEXT_COLOUR = (255, 220, 220)
            self.coin_text = self.font_coin.render(str(self.coins_earned_in_dungeon), True, self.COIN_TEXT_COLOUR)

            #Defining monsters killed text
            self.MONSTER_FONT_SIZE = 17
            self.MONSTER_TEXT_COLOUR = (220, 255, 220)
            self.font_monster = pygame.font.SysFont("Courier New", self.MONSTER_FONT_SIZE, bold=True)
            self.MONSTER_POSX = settings.SCREEN_WIDTH // 2 + 140
            self.MONSTER_POSY = settings.SCREEN_HEIGHT // 2 + 10
            self.monster_text = self.font_monster.render(str(self.monsters_killed_in_dungeon), True, self.MONSTER_TEXT_COLOUR)
        
        def custom_draw(self, screen):
            screen.blit(self.coin_text, (self.COIN_POSX, self.COIN_POSY))
            screen.blit(self.monster_text, (self.MONSTER_POSX, self.MONSTER_POSY))

class OverworldPauseMenu(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.type = "pauseMenu"
            self.menu_image = pygame.image.load(f"assets/hud/overworldPause/menu.png").convert()
            self.rect = self.menu_image.get_rect()

            self.menux = settings.SCREEN_WIDTH // 2 - self.rect.width // 2
            self.menuy = settings.SCREEN_HEIGHT // 2 - self.rect.height // 2

            self.quit_image = pygame.image.load(f"assets/hud/overworldPause/quit.png").convert_alpha()
            self.quit_button_hitbox_rect = self.quit_image.get_rect()
            
            self.quitx = self.menux + 4
            self.quity = self.menuy + 28
            self.quit_button_hitbox_rect.x = self.quitx
            self.quit_button_hitbox_rect.y = self.quity
                    
        def custom_draw(self, screen):
            screen.blit(self.menu_image, (self.menux, self.menuy))
            screen.blit(self.quit_image, (self.quitx, self.quity))

        def get_gamestate_world_and_pause_status_from_quit_button(self, input_events):
            for event in input_events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if self.quit_button_hitbox_rect.collidepoint(mouse_pos):
                        return "title", False
            return "overworld", True

class TitleMenu(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = "titleMenu"
        self.title_state = "title"

        self.title_screen = pygame.image.load('assets/splashscreens/titleScreen.png').convert_alpha()
        self.title_screen_rect = self.title_screen.get_rect()
        self.title_screen_rect.center = (settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)
        
        self.newgame_button = pygame.image.load('assets/hud/titleMenu/newGame.png').convert_alpha()
        self.newgame_button_rect = self.newgame_button.get_rect()
        self.newgame_button_rect.x = self.title_screen_rect.x + 189
        self.newgame_button_rect.y = self.title_screen_rect.y + 192

        self.loadgame_button = pygame.image.load('assets/hud/titleMenu/loadGame.png').convert_alpha()
        self.loadgame_button_rect = self.loadgame_button.get_rect()
        self.loadgame_button_rect.x = self.title_screen_rect.x + 350
        self.loadgame_button_rect.y = self.title_screen_rect.y + 192

        #******************************************************************************************
        # Load section 
        #******************************************************************************************
        scroll_button_side_offsets = 140
        worldoption_height_from_top_of_screen = 280
        self.scrollleft_button = pygame.image.load('assets/hud/titleMenu/scrollLeft.png').convert_alpha()
        self.scrollleft_button_rect = self.scrollleft_button.get_rect()
        self.scrollleft_button_rect.x = self.title_screen_rect.left + scroll_button_side_offsets
        self.scrollleft_button_rect.y = self.title_screen_rect.y + worldoption_height_from_top_of_screen

        self.scrollright_button = pygame.image.load('assets/hud/titleMenu/scrollRight.png').convert_alpha()
        self.scrollright_button_rect = self.scrollright_button.get_rect()
        self.scrollright_button_rect.x = self.title_screen_rect.right - scroll_button_side_offsets - self.scrollright_button_rect.width
        self.scrollright_button_rect.y = self.title_screen_rect.y + worldoption_height_from_top_of_screen

        self.worldoption_left = pygame.image.load('assets/hud/titleMenu/worldOption.png').convert_alpha()
        self.worldoption_left_rect = self.worldoption_left.get_rect()
        space_between_scroll_buttons = self.scrollright_button_rect.left - self.scrollleft_button_rect.right
        space_between_worldoptions = (space_between_scroll_buttons - 3*self.worldoption_left_rect.width) // 4
        self.worldoption_left_rect.x = self.scrollleft_button_rect.right + space_between_worldoptions
        self.worldoption_left_rect.y = self.title_screen_rect.y + worldoption_height_from_top_of_screen + 6

        self.worldoption_middle = pygame.image.load('assets/hud/titleMenu/worldOption.png').convert_alpha()
        self.worldoption_middle_rect = self.worldoption_middle.get_rect()
        self.worldoption_middle_rect.x = self.worldoption_left_rect.right + space_between_worldoptions
        self.worldoption_middle_rect.y = self.worldoption_left_rect.y

        self.worldoption_right = pygame.image.load('assets/hud/titleMenu/worldOption.png').convert_alpha()
        self.worldoption_right_rect = self.worldoption_right.get_rect()
        self.worldoption_right_rect.x = self.worldoption_middle_rect.right + space_between_worldoptions
        self.worldoption_right_rect.y = self.worldoption_left_rect.y

        self.back_button = pygame.image.load('assets/hud/titleMenu/buttonBack.png').convert_alpha()
        self.back_button_rect = self.back_button.get_rect()
        self.back_button_rect.x = self.scrollleft_button_rect.x
        self.back_button_rect.y = self.loadgame_button_rect.y + 380

        self.world_options_nonblanks = []
        self.world_options_total = []
        self.world_list_index_current = 0
        self.scrollleft_active = False
        self.scrollright_active = False
        self.player_selected_option = None

        #Select World Text
        self.SELECTWORLD_FONT_SIZE = 15
        self.SELECTWORLD_FONT_COLOUR = (0, 0, 0)
        self.FONT_SELECTWORLD = pygame.font.SysFont("Courier New", self.SELECTWORLD_FONT_SIZE, bold=True)        
        self.SELECTWORLD_TEXT = self.FONT_SELECTWORLD.render(str("Select World:"), True, self.SELECTWORLD_FONT_COLOUR)
        self.SELECTWORLD_TEXT_POSY = self.worldoption_middle_rect.y - 48
        self.SELECTWORLD_TEXT_POSX = settings.SCREEN_WIDTH // 2 - self.SELECTWORLD_TEXT.get_width() // 2 

        #Defining world_name font appearances
        self.WORLD_NAME_FONT_SIZE = 11
        self.WORLD_NAME_FONT_COLOUR = (0, 0, 0)
        self.FONT_WORLD_NAME = pygame.font.SysFont("Courier New", self.WORLD_NAME_FONT_SIZE, bold=True)
        self.WORLD_NAME_TEXT_POSY = self.worldoption_left_rect.bottom + 4
        
        self.world_name_left_text_pos_x = 9999
        self.world_name_mid_text_pos_x = 9999
        self.world_name_right_text_pos_x = 9999
        
        self.world_name_left_text = None
        self.world_name_mid_text = None
        self.world_name_right_text = None

        #Load Game play button
        self.loadgameplay_button = pygame.image.load('assets/hud/titleMenu/loadGame.png').convert_alpha()
        self.loadgameplay_button_rect = self.loadgame_button.get_rect()
        self.loadgameplay_button_rect.x = self.worldoption_middle_rect.centerx - self.loadgameplay_button_rect.width // 2
        self.loadgameplay_button_rect.y = self.worldoption_middle_rect.bottom + 30

        #******************************************************************************************
        # New game section 
        #******************************************************************************************

        self.NEWGAME_MENU_FONT_SIZE = self.SELECTWORLD_FONT_SIZE
        self.NEWGAME_MENU_FONT_COLOUR = (0, 0, 0)
        self.FONT_NEWGAME_MENU = pygame.font.SysFont("Courier New", self.NEWGAME_MENU_FONT_SIZE, bold=True)        
        self.NEWGAME_MENU_TEXT = self.FONT_NEWGAME_MENU.render(str("Type new world name:"), True, self.NEWGAME_MENU_FONT_COLOUR)
        self.NEWGAME_MENU_TEXT_POSY = self.SELECTWORLD_TEXT_POSY
        self.NEWGAME_MENU_TEXT_POSX = settings.SCREEN_WIDTH // 2 - self.NEWGAME_MENU_TEXT.get_width() // 2 

        self.newgame_text_entry_bar = pygame.image.load('assets/hud/titleMenu/textEntryBar.png').convert_alpha()
        self.newgame_text_entry_bar_rect = self.newgame_text_entry_bar.get_rect()
        self.newgame_text_entry_bar_rect.x = settings.SCREEN_WIDTH // 2 - (self.newgame_text_entry_bar_rect.width // 2)
        self.newgame_text_entry_bar_rect.y = self.NEWGAME_MENU_TEXT_POSY + 50

        self.worldname_text_entered = ""

        self.TEXT_ENTRY_FONT_SIZE = self.SELECTWORLD_FONT_SIZE
        self.TEXT_ENTRY_FONT_COLOUR = (0, 0, 0)
        self.FONT_TEXT_ENTRY = pygame.font.SysFont("Courier New", self.TEXT_ENTRY_FONT_SIZE, bold=True)        
        self.TEXT_ENTRY_TEXT = self.FONT_TEXT_ENTRY.render(str(self.worldname_text_entered), True, self.TEXT_ENTRY_FONT_COLOUR)
        self.TEXT_ENTRY_TEXT_POSY = self.newgame_text_entry_bar_rect.y + 14
        self.TEXT_ENTRY_TEXT_POSX = self.newgame_text_entry_bar_rect.x + 9

        self.newgame_text_underscore = pygame.image.load('assets/hud/titleMenu/underscore.png').convert_alpha()
        self.newgame_text_underscore_rect = self.newgame_text_underscore.get_rect()

        self.newgame_confirm_button = pygame.image.load('assets/hud/titleMenu/newGame.png').convert_alpha()
        self.newgame_confirm_button_rect = self.newgame_confirm_button.get_rect()
        self.newgame_confirm_button_rect.x = settings.SCREEN_WIDTH // 2 - (self.newgame_confirm_button_rect.width // 2)
        self.newgame_confirm_button_rect.y = self.newgame_text_entry_bar_rect.bottom + 40

    def handle_worldname_text_input(self, input_events):
        mods = pygame.key.get_mods()
        for event in input_events:
            if event.type == pygame.KEYDOWN:
                if len(self.worldname_text_entered) < settings.MAX_WORLDNAME_LENGTH:
                    if mods & pygame.KMOD_LSHIFT or mods & pygame.KMOD_CAPS:                    
                        self.worldname_text_entered += settings.allowed_keystrokes.get(event.key, "").upper()
                    else:
                        self.worldname_text_entered += settings.allowed_keystrokes.get(event.key, "")

                if event.key == pygame.K_BACKSPACE and len(self.worldname_text_entered) > 0:
                    self.worldname_text_entered = self.worldname_text_entered[:-1]

    def refresh_worldname_text_drawn(self, screen):
        self.FONT_TEXT_ENTRY = pygame.font.SysFont("Courier New", self.TEXT_ENTRY_FONT_SIZE, bold=True)        
        self.TEXT_ENTRY_TEXT = self.FONT_TEXT_ENTRY.render(str(self.worldname_text_entered), True, self.TEXT_ENTRY_FONT_COLOUR)
        self.newgame_text_underscore_rect.x = self.TEXT_ENTRY_TEXT_POSX + self.TEXT_ENTRY_TEXT.get_width() + 2
        self.newgame_text_underscore_rect.y = self.TEXT_ENTRY_TEXT_POSY + self.TEXT_ENTRY_TEXT.get_height() - 7
        if len(self.worldname_text_entered) < settings.MAX_WORLDNAME_LENGTH:
            screen.blit(self.newgame_text_underscore, self.newgame_text_underscore_rect.topleft)

    def title_draw(self, screen):
        screen.blit(self.title_screen, self.title_screen_rect.topleft)
        screen.blit(self.newgame_button, self.newgame_button_rect.topleft)
        screen.blit(self.loadgame_button, self.loadgame_button_rect.topleft)

    def load_screen_worldname_draw(self, screen):
        """Determines the positions of texts to appear centered under blocks, and determines the 3 world texts to be shown based on current scroll index."""
        #Getting names
        name_left = self.world_options_total[self.world_list_index_current]
        name_mid = self.world_options_total[self.world_list_index_current + 1]
        name_right = self.world_options_total[self.world_list_index_current + 2]
        #Rendering names in background
        self.world_name_left_text = self.FONT_WORLD_NAME.render(str(name_left), True, self.WORLD_NAME_FONT_COLOUR)
        self.world_name_mid_text = self.FONT_WORLD_NAME.render(str(name_mid), True, self.WORLD_NAME_FONT_COLOUR)
        self.world_name_right_text = self.FONT_WORLD_NAME.render(str(name_right), True, self.WORLD_NAME_FONT_COLOUR)
        #Getting widths (for centering)
        name_left_width = self.world_name_left_text.get_width()
        name_mid_width = self.world_name_mid_text.get_width()
        name_right_width = self.world_name_right_text.get_width()

        self.world_name_left_text_pos_x = self.worldoption_left_rect.centerx - name_left_width // 2
        self.world_name_mid_text_pos_x = self.worldoption_middle_rect.centerx - name_mid_width // 2
        self.world_name_right_text_pos_x = self.worldoption_right_rect.centerx - name_right_width // 2

        screen.blit(self.world_name_left_text, (self.world_name_left_text_pos_x, self.WORLD_NAME_TEXT_POSY))
        screen.blit(self.world_name_mid_text, (self.world_name_mid_text_pos_x, self.WORLD_NAME_TEXT_POSY))
        screen.blit(self.world_name_right_text, (self.world_name_right_text_pos_x, self.WORLD_NAME_TEXT_POSY))

    def handle_selected_world_option(self, screen, input_events):
        def reset_world_images():
            self.worldoption_left = pygame.image.load('assets/hud/titleMenu/worldOption.png').convert_alpha()
            self.worldoption_middle = pygame.image.load('assets/hud/titleMenu/worldOption.png').convert_alpha()
            self.worldoption_right = pygame.image.load('assets/hud/titleMenu/worldOption.png').convert_alpha()
        selection = self.player_selected_option
        for event in input_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.worldoption_left_rect.collidepoint(mouse_pos):
                    selection = "left"
                elif self.worldoption_middle_rect.collidepoint(mouse_pos):
                    selection = "middle"
                elif self.worldoption_right_rect.collidepoint(mouse_pos):
                    selection = "right"
        if selection != self.player_selected_option:
            reset_world_images()
            self.player_selected_option = selection
            if selection == "left":
                 self.worldoption_left = pygame.image.load('assets/hud/titleMenu/worldOptionSelect.png').convert_alpha()
            elif selection == "middle":
                 self.worldoption_middle = pygame.image.load('assets/hud/titleMenu/worldOptionSelect.png').convert_alpha()
            elif selection == "right":
                 self.worldoption_right = pygame.image.load('assets/hud/titleMenu/worldOptionSelect.png').convert_alpha() 

    def determine_scroll_buttons_shown(self, input_events, screen):
        if self.world_list_index_current != 0:
            screen.blit(self.scrollleft_button, self.scrollleft_button_rect.topleft)
            self.scrollleft_active = True
        else:
            self.scrollleft_active = False
        if self.world_list_index_current + 2 < len(self.world_options_total) - 1:
            screen.blit(self.scrollright_button, self.scrollright_button_rect.topleft)
            self.scrollright_active = True
        else:
            self.scrollright_active = False

    def handle_scroll_button_presses(self, input_events):
        for event in input_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.scrollleft_button_rect.collidepoint(mouse_pos) and self.scrollleft_active:
                    self.world_list_index_current -= 1
                elif self.scrollright_button_rect.collidepoint(mouse_pos) and self.scrollright_active:
                    self.world_list_index_current += 1

    def load_screen_draw(self, screen, input_events):
        screen.blit(self.title_screen, self.title_screen_rect.topleft)
        screen.blit(self.back_button, self.back_button_rect.topleft)
        self.determine_scroll_buttons_shown(input_events, screen)
        self.handle_scroll_button_presses(input_events)
        self.load_screen_worldname_draw(screen)
        self.handle_selected_world_option(screen, input_events)
        if len(self.world_options_nonblanks) > 0:
            screen.blit(self.worldoption_left, self.worldoption_left_rect.topleft)
        if len(self.world_options_nonblanks) > 1:
            screen.blit(self.worldoption_middle, self.worldoption_middle_rect.topleft)
        if len(self.world_options_nonblanks) > 2:
            screen.blit(self.worldoption_right, self.worldoption_right_rect.topleft)
        screen.blit(self.SELECTWORLD_TEXT, (self.SELECTWORLD_TEXT_POSX, self.SELECTWORLD_TEXT_POSY))
        screen.blit(self.loadgameplay_button, (self.loadgameplay_button_rect.x, self.loadgameplay_button_rect.y))

    def handle_new_game_creation_button_titlestate(self, input_events):
         for event in input_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.title_state == "newgamemenu":
                    if self.newgame_confirm_button_rect.collidepoint(mouse_pos) and len(self.worldname_text_entered) != 0:
                        self.title_state = "newgamecreated"


    def newgame_menu_draw(self, screen, input_events):
        self.handle_worldname_text_input(input_events)
        screen.blit(self.title_screen, self.title_screen_rect.topleft)
        screen.blit(self.back_button, self.back_button_rect.topleft)
        screen.blit(self.NEWGAME_MENU_TEXT, (self.NEWGAME_MENU_TEXT_POSX, self.NEWGAME_MENU_TEXT_POSY))
        screen.blit(self.newgame_text_entry_bar, self.newgame_text_entry_bar_rect.topleft)
        screen.blit(self.TEXT_ENTRY_TEXT, (self.TEXT_ENTRY_TEXT_POSX, self.TEXT_ENTRY_TEXT_POSY))
        screen.blit(self.newgame_confirm_button, self.newgame_confirm_button_rect.topleft)
        self.refresh_worldname_text_drawn(screen)
        self.handle_new_game_creation_button_titlestate(input_events)

    def fetch_savefile_names(self):
        files_and_modified_times = []
        sorted_files = []
        folder_path = "saves"

        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                file_path = os.path.join(folder_path, filename)
                last_modified_time = os.path.getmtime(file_path)
                
                files_and_modified_times.append((last_modified_time, os.path.splitext(filename)[0]))
        
        #Sorting by last modified time, so most recent files are shown first.
        files_and_modified_times.sort(key=lambda x: x[0])
        files_and_modified_times.reverse()
        sorted_files = [filename[1] for filename in files_and_modified_times]

        #Adding blank file names to the list (these do not pull back save files, but stop any risk of overflow)
        self.world_options_nonblanks = [i for i in sorted_files]
        if len(sorted_files) < 3:
            for i in range(0, 3 - len(sorted_files)):
                sorted_files.append("")
        self.world_options_total = sorted_files

    def check_back_button_pressed_set_title_state(self, input_events):
        if self.title_state not in ["loadpage", "newgamemenu"]:
            return
        for event in input_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.back_button_rect.collidepoint(mouse_pos):
                    self.title_state = "title"

    def custom_draw(self, screen, input_events):
        self.check_back_button_pressed_set_title_state(input_events)
        if self.title_state == "title":
            self.title_draw(screen)
        elif self.title_state == "loadpage":
            self.load_screen_draw(screen, input_events)
        elif self.title_state == "newgamemenu":
            self.newgame_menu_draw(screen, input_events)
    
    def get_newgame_or_loadgame_or_loadgameselection_clicked(self, input_events):
        for event in input_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.title_state == "title":
                    if self.loadgame_button_rect.collidepoint(mouse_pos):
                        self.title_state = "loadpage"
                        self.fetch_savefile_names()
                        return None
                    elif self.newgame_button_rect.collidepoint(mouse_pos):
                        self.title_state = "newgamemenu"
                        self.worldname_text_entered = ""
                        return None
                elif self.title_state == "loadpage":
                    if self.loadgameplay_button_rect.collidepoint(mouse_pos):
                        if self.player_selected_option is not None:
                            return "loadgamefile"
                elif self.title_state == "newgamecreated":
                    return "newgamecreated"
        return None
    
    def get_selected_world_name(self):
        base_world = self.world_list_index_current
        offset = 0
        if self.player_selected_option == "left":
            offset = 0
        elif self.player_selected_option == "middle":
            offset = 1
        elif self.player_selected_option == "right":
            offset = 2
        selected_world = self.world_options_total[base_world + offset]

        return selected_world
    
class ShopMenu(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = "shopMenu"

        self.shop_menu = pygame.image.load('assets/hud/purchaseMenu/shopMenu.png').convert_alpha()
        self.shop_menu_rect = self.shop_menu.get_rect()
        self.shop_menu_rect.x = settings.SCREEN_WIDTH // 2 - self.shop_menu_rect.width // 2
        self.shop_menu_rect.y = settings.SCREEN_HEIGHT // 2 - self.shop_menu_rect.height // 2

        self.hover_sound_played = False
        self.open_sound_played = False

        self.ITEMS_PER_ROW = 3
        self.MAX_ITEM_WIDTHHEIGHT = 40
        self.SPACE_BETWEEN_OPTIONS = (self.shop_menu_rect.width - 3 * self.MAX_ITEM_WIDTHHEIGHT) // (1 + self.ITEMS_PER_ROW)

        self.shop_options = {
            1: {
                "item": "overgroundGrass",
                "imageLink": "assets/overworldtiles/overgroundGrass.png",
                "cost": 1,
                "type": "secondary",
            },
            2: {
                "item": "tinyPot",
                "imageLink": "assets/overworldtiles/tinyPot.png",
                "cost": 4,
                "type": "primary",
            },
            3: {
                "item": "tinyFlower",
                "imageLink": "assets/overworldtiles/tinyFlower.png",
                "cost": 10,
                "type": "primary",
            },
            4: {
                "item": "cobblestone",
                "imageLink": "assets/overworldtiles/cobblestone.png",
                "cost": 2,
                "type": "primary",
            },
            5: {
                "item": "bench",
                "imageLink": "assets/hud/buildthumbnails/bench.png",
                "cost": 8,
                "type": "primary", 
            }
        }
        self.shop_item_count = len(self.shop_options.keys())

        self.purchase_delivery_pending = False
        self.purchased_item = None
        self.purchased_amount = 0
        self.purchased_cost = 0

        self.button_shell_rect_offset_x = -5
        self.button_shell_font_size = 12
        self.button_shell_font = pygame.font.SysFont("Courier New", self.button_shell_font_size, bold=True)
        self.button_shell_font_colour = (0, 0, 0)

        self.coin_cost_font_size = 11
        self.coin_cost_font = pygame.font.SysFont("Courier New", self.coin_cost_font_size, bold=True)

        self.b_button = pygame.image.load('assets/hud/purchaseMenu/B.png').convert_alpha()
        self.b_button_rect = self.b_button.get_rect()
        self.b_button_rect.topleft = settings.OVERWORLD_SHOPKEEPER_COORDS

        item_count = 0
        for key in self.shop_options.keys():
            self.shop_options[key]["image"] = pygame.image.load(self.shop_options[key]["imageLink"]).convert_alpha()
            self.shop_options[key]["rect"] = self.shop_options[key]["image"].get_rect()
            self.shop_options[key]["width"] = self.shop_options[key]["rect"].width
            self.shop_options[key]["height"] = self.shop_options[key]["rect"].height
            self.shop_options[key]["count"] = item_count
            self.shop_options[key]["row"] = item_count // self.ITEMS_PER_ROW
            self.shop_options[key]["column"] = item_count % self.ITEMS_PER_ROW
            self.shop_options[key]["rect"].x = self.shop_menu_rect.x + self.SPACE_BETWEEN_OPTIONS + self.shop_options[key]["column"] * (self.SPACE_BETWEEN_OPTIONS + self.MAX_ITEM_WIDTHHEIGHT) + self.MAX_ITEM_WIDTHHEIGHT // 2 - self.shop_options[key]["width"] // 2
            self.shop_options[key]["rect"].y = self.shop_menu_rect.y + 10 + self.SPACE_BETWEEN_OPTIONS + self.shop_options[key]["row"] * (self.SPACE_BETWEEN_OPTIONS + self.MAX_ITEM_WIDTHHEIGHT) + self.MAX_ITEM_WIDTHHEIGHT // 2 - self.shop_options[key]["height"] // 2
            
            self.shop_options[key]["button_shell"] = pygame.image.load("assets/hud/purchaseMenu/buttonShell.png").convert_alpha()
            self.shop_options[key]["button_shell_rect"] = self.shop_options[key]["button_shell"].get_rect()
            self.shop_options[key]["button_shell_rect"].x = self.shop_options[key]["rect"].x - self.shop_options[key]["button_shell_rect"].width + self.button_shell_rect_offset_x
            self.shop_options[key]["button_shell_rect"].y = self.shop_options[key]["rect"].centery - self.shop_options[key]["button_shell_rect"].height // 2
            
            self.shop_options[key]["button_shell_font_image"] = self.button_shell_font.render(str(item_count + 1), True, self.button_shell_font_colour)
            self.shop_options[key]["button_shell_font_image_rect"] = self.shop_options[key]["button_shell_font_image"].get_rect()
            self.shop_options[key]["button_shell_font_image_rect"].x = self.shop_options[key]["button_shell_rect"].x + self.shop_options[key]["button_shell_font_image_rect"].width // 2
            self.shop_options[key]["button_shell_font_image_rect"].y = self.shop_options[key]["button_shell_rect"].centery - self.shop_options[key]["button_shell_font_image_rect"].height // 2 + 1

            coins = self.shop_options[key]["cost"]
            cointext = "coin" if coins == 1 else "coins"
            self.shop_options[key]["coin_cost_font_image"] = self.coin_cost_font.render(str(f"{coins} {cointext}"), True, self.button_shell_font_colour)
            self.shop_options[key]["coin_cost_font_image_rect"] = self.shop_options[key]["coin_cost_font_image"].get_rect()
            self.shop_options[key]["coin_cost_font_image_rect"].x = self.shop_options[key]["rect"].centerx - self.shop_options[key]["coin_cost_font_image_rect"].width // 2
            self.shop_options[key]["coin_cost_font_image_rect"].y = self.shop_options[key]["rect"].bottom + 6
            
            item_count += 1

    def play_menu_open_sfx(self):
        sfx = pygame.mixer.Sound(f"assets/sfx/hud/menuOpen.mp3")
        sfx.play()
    def play_insufficient_coins_sfx(self):
        sfx = pygame.mixer.Sound(f"assets/sfx/hud/menuError.mp3")
        sfx.play()
    def play_transaction_sfx(self):
        sfx = pygame.mixer.Sound(f"assets/sfx/hud/transaction.mp3")
        sfx.play()

    def draw_available_shop_options(self, screen):
        for key in self.shop_options.keys():
            screen.blit(self.shop_options[key]["image"], self.shop_options[key]["rect"].topleft)
            screen.blit(self.shop_options[key]["button_shell"], self.shop_options[key]["button_shell_rect"].topleft)
            screen.blit(self.shop_options[key]["button_shell_font_image"], self.shop_options[key]["button_shell_font_image_rect"].topleft)
            screen.blit(self.shop_options[key]["coin_cost_font_image"], self.shop_options[key]["coin_cost_font_image_rect"].topleft)

    def detect_player_shop_keydown(self, input_events, player_coins):
        key = None
        for event in input_events:    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                elif event.key == pygame.K_2:
                    key = 2
                elif event.key == pygame.K_3:
                    key = 3
                elif event.key == pygame.K_4:
                    key = 4
                elif event.key == pygame.K_5:
                    key = 5
                elif event.key == pygame.K_6:
                    key = 6
                elif event.key == pygame.K_7:
                    key = 7
                elif event.key == pygame.K_8:
                    key = 8
                elif event.key == pygame.K_9:
                    key = 9
        if key is not None and key <= self.shop_item_count:
            self.save_player_purchase_in_state(key, player_coins)

    def save_player_purchase_in_state(self, purchase_key, player_coins):
        purchase_amount = 1
        cost = self.shop_options[purchase_key]["cost"] * purchase_amount
        if cost <= player_coins:
            self.purchased_amount = purchase_amount
            self.purchased_item = self.shop_options[purchase_key]["item"]
            self.purchased_cost = cost
            self.purchase_delivery_pending = True
            self.play_transaction_sfx()
        else:
            self.play_insufficient_coins_sfx()
        
    def reset_purchase_state(self):
        self.purchased_amount = 0
        self.purchased_item = None
        self.purchased_cost = 0
        self.purchase_delivery_pending = False

    def get_purchased_items_and_cost(self):
        if not self.purchase_delivery_pending:
            return ["overgroundGrass", 0, 0]

        result = [self.purchased_item, self.purchased_amount, self.purchased_cost]

        self.reset_purchase_state()

        return result

    def _draw_b_menu_button_near_shop(self, screen, camera_offset):
        xplacement = self.b_button_rect.x - camera_offset[0] - 20
        yplacement = self.b_button_rect.y - camera_offset[1] - 50
        screen.blit(self.b_button, (xplacement, yplacement))
        if not self.hover_sound_played:
            self.play_menu_open_sfx()
            self.hover_sound_played = True

    def custom_update_and_draw(self, player_in_shop_range, screen, input_events, player_coins, player_in_build_mode, camera_offset):
        if not player_in_shop_range:
            self.hover_sound_played = False
            self.open_sound_played = False
            return
        
        if not player_in_build_mode:
            self._draw_b_menu_button_near_shop(screen, camera_offset)
            return

        if not self.open_sound_played:
            self.play_menu_open_sfx()
            self.open_sound_played = True
        
        screen.blit(self.shop_menu, self.shop_menu_rect.topleft)
        self.draw_available_shop_options(screen)
        self.detect_player_shop_keydown(input_events, player_coins)