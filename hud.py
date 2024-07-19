import pygame
import settings
import os
import json


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

class OverworldHud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = "hud"
        self.image = pygame.image.load("assets/hud/hudbar.png").convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.x = settings.SCREEN_WIDTH - self.rect.w
        self.rect.y = settings.SCREEN_HEIGHT - self.rect.h

class BuildHud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/hud/buildhudbar.png").convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.x = 2*settings.SCREEN_WIDTH
        self.rect.y = 100
        
    def show(self):
        self.rect.x = settings.SCREEN_WIDTH - self.rect.w

    def hide(self):
        #There must be a better way to do this
        self.rect.x = 2*settings.SCREEN_WIDTH

class OverworldCoinText(pygame.sprite.Sprite):
    def __init__(self, hudx, hudy, coincount):
        super().__init__()
        self.font_size = 12
        self.font = pygame.font.SysFont("Calibri", self.font_size)
        self.font_colour = (0, 0, 0)
        self.hudx = hudx
        self.hudy = hudy
        self.hud_xoffset = 150
        self.hud_yoffset = 15
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

        #Load section
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
        self.worldoption_left_rect.y = self.title_screen_rect.y + worldoption_height_from_top_of_screen - 6

        self.worldoption_middle = pygame.image.load('assets/hud/titleMenu/worldOption.png').convert_alpha()
        self.worldoption_middle_rect = self.worldoption_middle.get_rect()
        self.worldoption_middle_rect.x = self.worldoption_left_rect.right + space_between_worldoptions
        self.worldoption_middle_rect.y = self.worldoption_left_rect.y

        self.worldoption_right = pygame.image.load('assets/hud/titleMenu/worldOption.png').convert_alpha()
        self.worldoption_right_rect = self.worldoption_right.get_rect()
        self.worldoption_right_rect.x = self.worldoption_middle_rect.right + space_between_worldoptions
        self.worldoption_right_rect.y = self.worldoption_left_rect.y

        self.world_options_total = []
        self.world_list_index_current = 0
        self.player_selected_option = None

        #Select World Text
        self.SELECTWORLD_FONT_SIZE = 15
        self.SELECTWORLD_FONT_COLOUR = (0, 0, 0)
        self.FONT_SELECTWORLD = pygame.font.SysFont("Courier New", self.SELECTWORLD_FONT_SIZE, bold=True)        
        self.SELECTWORLD_TEXT = self.FONT_SELECTWORLD.render(str("Select World:"), True, self.SELECTWORLD_FONT_COLOUR)
        self.SELECTWORLD_TEXT_POSY = self.worldoption_middle_rect.y - 26
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

    def handle_scroll_button_presses(self, input_events):
        pass


    def load_screen_draw(self, screen, input_events):
        screen.blit(self.title_screen, self.title_screen_rect.topleft)
        screen.blit(self.scrollright_button, self.scrollright_button_rect.topleft)
        screen.blit(self.scrollleft_button, self.scrollleft_button_rect.topleft)
        screen.blit(self.worldoption_left, self.worldoption_left_rect.topleft)
        screen.blit(self.worldoption_middle, self.worldoption_middle_rect.topleft)
        screen.blit(self.worldoption_right, self.worldoption_right_rect.topleft)
        screen.blit(self.SELECTWORLD_TEXT, (self.SELECTWORLD_TEXT_POSX, self.SELECTWORLD_TEXT_POSY))
        screen.blit(self.loadgameplay_button, (self.loadgameplay_button_rect.x, self.loadgameplay_button_rect.y))
        self.handle_scroll_button_presses(input_events)
        self.load_screen_worldname_draw(screen)
        self.handle_selected_world_option(screen, input_events)

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

        self.world_options_total = sorted_files
        print(self.world_options_total)

    def custom_draw(self, screen, input_events):
        if self.title_state == "title":
            self.title_draw(screen)
        elif self.title_state == "loadpage":
            self.load_screen_draw(screen, input_events)
    
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
                        return "newgame"
                elif self.title_state == "loadpage":
                    if self.loadgameplay_button_rect.collidepoint(mouse_pos):
                        if self.player_selected_option is not None:
                            return "loadgamefile"
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

        print(selected_world)
        return selected_world