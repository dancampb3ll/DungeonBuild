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

        self.sound_played = False
        
        self.ITEMS_PER_ROW = 3
        self.MAX_ITEM_WIDTHHEIGHT = 40
        self.SPACE_BETWEEN_OPTIONS = (self.shop_menu_rect.width - 3 * self.MAX_ITEM_WIDTHHEIGHT) // (1 + self.ITEMS_PER_ROW)

        self.shop_options = {
            "overworldGrass": {
                "imageLink": "assets/overworldtiles/overgroundGrass.png",
                "cost": 1,
                "type": "secondary"
            },
            "tinyPot": {
                "imageLink": "assets/overworldtiles/tinyPot.png",
                "cost": 10,
                "type": "primary"
            }
        }


        self.button_shell_rect_offset_x = -5
        self.button_shell_font_size = 12
        self.button_shell_font = pygame.font.SysFont("Courier New", self.button_shell_font_size, bold=True)
        self.button_shell_font_colour = (0, 0, 0)

        self.coin_cost_font_size = 11
        self.coin_cost_font = pygame.font.SysFont("Courier New", self.coin_cost_font_size, bold=True)

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

    def draw_available_shop_options(self, screen):
        for key in self.shop_options.keys():
            print(key, " ", self.shop_options[key]["count"])
            screen.blit(self.shop_options[key]["image"], self.shop_options[key]["rect"].topleft)
            screen.blit(self.shop_options[key]["button_shell"], self.shop_options[key]["button_shell_rect"].topleft)
            screen.blit(self.shop_options[key]["button_shell_font_image"], self.shop_options[key]["button_shell_font_image_rect"].topleft)
            screen.blit(self.shop_options[key]["coin_cost_font_image"], self.shop_options[key]["coin_cost_font_image_rect"].topleft)

    def custom_draw(self, player_in_shop_range, screen):
        if not player_in_shop_range:
            self.sound_played = False
            return
        if not self.sound_played:
            self.play_menu_open_sfx()
        self.sound_played = True
        screen.blit(self.shop_menu, self.shop_menu_rect.topleft)
        self.draw_available_shop_options(screen)

