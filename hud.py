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
        self.coins_earned_in_dungeon = 2

        #Defining Healthbars
        self.GREEN_HEALTHBAR_START_PIXELX = self.rect.x + 8
        self.GREEN_HEALTHBAR_START_PIXELY = self.rect.y + 9
        self.GREEN_HEALTHBAR_WIDTH = 210
        self.GREEN_HEALTHBAR_HEIGHT = 10
        self.healthrect_green = pygame.Rect(self.GREEN_HEALTHBAR_START_PIXELX, self.GREEN_HEALTHBAR_START_PIXELY, self.GREEN_HEALTHBAR_WIDTH, self.GREEN_HEALTHBAR_HEIGHT)
        
        self.RED_HEALTHBAR_END_PIXELX = self.GREEN_HEALTHBAR_START_PIXELX + self.GREEN_HEALTHBAR_WIDTH + 1
        self.RED_HEALTHBAR_START_PIXELY = self.GREEN_HEALTHBAR_START_PIXELY
        self.red_healthbar_start_pixelx = self.RED_HEALTHBAR_END_PIXELX
        self.RED_HEALTHBAR_HEIGHT = self.GREEN_HEALTHBAR_HEIGHT
        self.RED_HEALTHBAR_WIDTH = 0
        self.healthrect_red = pygame.Rect(self.red_healthbar_start_pixelx, self.RED_HEALTHBAR_START_PIXELY, self.RED_HEALTHBAR_WIDTH, self.RED_HEALTHBAR_HEIGHT)

        #Defining health_text
        self.HEALTH_FONT_SIZE = 12
        self.HEALTH_TEXT_COLOUR = (30, 30, 30)
        self.font_health = pygame.font.SysFont("OpenSans-Bold.ttf", self.HEALTH_FONT_SIZE, bold=True)
        self.HEALTH_POSX = settings.SCREEN_WIDTH // 2 - 8
        self.HEALTH_POSY = settings.SCREEN_HEIGHT - 26
        self.health_text = self.font_health.render(str(self.health), True, self.HEALTH_TEXT_COLOUR)

        #Defining coincount
        self.COIN_FONT_SIZE = 14
        self.COIN_POSX = settings.SCREEN_WIDTH // 2 - 107
        self.COIN_POSY = settings.SCREEN_HEIGHT - 14
        self.font_coin = pygame.font.SysFont("OpenSans-Bold.ttf", self.COIN_FONT_SIZE, bold=True)
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

    

    def custom_draw(self, screen):
        #Healthbars
        pygame.draw.rect(screen, (100, 255, 100), self.healthrect_green, 0)
        pygame.draw.rect(screen, (255, 100, 100), self.healthrect_red, 0)

        #Health Text
        screen.blit(self.health_text, (self.HEALTH_POSX, self.HEALTH_POSY))

        #Coin text
        screen.blit(self.coin_text, (self.COIN_POSX, self.COIN_POSY))

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
