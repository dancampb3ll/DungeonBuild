import pygame
import settings

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
                        print("clicked")
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

    def title_draw(self, screen):
        screen.blit(self.title_screen, self.title_screen_rect.topleft)
        screen.blit(self.newgame_button, self.newgame_button_rect.topleft)
        screen.blit(self.loadgame_button, self.loadgame_button_rect.topleft)

    def custom_draw(self, screen):
        if self.title_state == "title":
            self.title_draw(screen)
    
    def get_newgame_or_loadgame_clicked(self, input_events):
        for event in input_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.loadgame_button_rect.collidepoint(mouse_pos):
                    return "loadgame"
                elif self.newgame_button_rect.collidepoint(mouse_pos):
                    return "newgame"
        return None
        