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

class FloatingHud(pygame.sprite.Sprite):
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
