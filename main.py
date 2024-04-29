import pygame
import overworldtiles

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
TILE_SIZE = 16
TILE_COUNT = SCREEN_HEIGHT / TILE_SIZE
PLAYERSPEED = 1
CAMERASPEED = PLAYERSPEED
WALKABLE = overworldtiles.walkable

#A tile is initialised with a gridx and gridy location. The true x and true y are then multiples of these by the tile size.
class OutdoorTile(pygame.sprite.Sprite):
    def __init__(self, gridx, gridy, tile, pygame_group):
        super().__init__(pygame_group)
        self.image = pygame.image.load(f"assets/{tile}.png").convert()
        self.rect = self.image.get_rect()
        self.gridx = gridx
        self.gridy = gridy
        self.rect.x = gridx * TILE_SIZE
        self.rect.y = gridy * TILE_SIZE
    
    def update(self):
        None
    

class Player(pygame.sprite.Sprite):
    def __init__(self, pygame_group):
        super().__init__(pygame_group)
        self.image = pygame.image.load("assets/player.png").convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT // 2
        self.debug = ""

    def move_player(self, overworldmapdict, tile_mappings):
        key = pygame.key.get_pressed()
        #left
        if key[pygame.K_a]:
            check = self.rect.midleft
            tilename = overworldtiles.get_world_tilename_at_xy_from_mappingsdict(check, overworldmapdict, tile_mappings, TILE_SIZE)
            if tilename in WALKABLE:
                self.rect.x -= PLAYERSPEED
        #right
        elif key[pygame.K_d]:
            check = self.rect.midright
            tilename = overworldtiles.get_world_tilename_at_xy_from_mappingsdict(check, overworldmapdict, tile_mappings, TILE_SIZE)
            if tilename in WALKABLE:
                self.rect.x += PLAYERSPEED
        #down
        if key[pygame.K_s]:
            check = self.rect.midbottom
            tilename = overworldtiles.get_world_tilename_at_xy_from_mappingsdict(check, overworldmapdict, tile_mappings, TILE_SIZE)
            if tilename in WALKABLE:
                self.rect.y += PLAYERSPEED
        #up
        elif key[pygame.K_w]:
            check = self.rect.midtop
            tilename = overworldtiles.get_world_tilename_at_xy_from_mappingsdict(check, overworldmapdict, tile_mappings, TILE_SIZE)
            if tilename in WALKABLE:
                self.rect.y -= PLAYERSPEED

    def update(self):
        #print((self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE))
        debug = f"self.rect.center {self.rect.center} | self.rect.bottomleft {self.rect.bottomleft} | self.rect.topright {self.rect.topright} | self.rect.center tile {self.rect.center[0] // (TILE_SIZE)} | self.rect.bottomleft tile {self.rect.bottomleft[0] // TILE_SIZE} | self.rect.topright tile {self.rect.topright[0] // TILE_SIZE}"
        if debug != self.debug:
            self.debug = debug
            print(self.debug)

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        self.offset = pygame.math.Vector2(0, 0)
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2

    def center_target_camera(self,target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def custom_draw(self, target):
        self.center_target_camera(target)
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

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
        self.material = tiledict[self.tile]
        self.text = f"Player x on grid: {self.playergridx} | Player y on grid: {self.playergridy} | Map material at x,y: {self.material}"
        self.image = self.font.render(self.text, True, self.font_colour)
        self.rect = self.image.get_rect(topleft = (5, 5))


pygame.init()
 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

pygame.display.set_caption('DungeonBuild')


#Camera must be defined first
cameragroup = CameraGroup()

#Drawing tiles
#debug grid
debuggrid = False
if debuggrid:
    for i in range(0, 40):
        for j in range(0, 40):
            OutdoorTile(i, j, "overgroundGrid", cameragroup)

overworldmap = overworldtiles.overworldmap
overworldmapdict = overworldtiles.overworldmapdict
tile_mappings = overworldtiles.tile_mappings

for tile in overworldmap:
    i = tile[0]
    j = tile[1]
    tiletype = tile[2]
    if tiletype != 0:
        tilename = tile_mappings[tiletype]
        OutdoorTile(i, j, tilename, cameragroup)
    


player = Player(cameragroup)

debugtext = DebugText()
screentext = pygame.sprite.Group()
screentext.add(debugtext)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((10, 10, 18))


    player.move_player(overworldmapdict, tile_mappings)

    cameragroup.update()
    cameragroup.custom_draw(player)

    debugtext.update(round(player.rect.x / TILE_SIZE), round(player.rect.y / TILE_SIZE), overworldmapdict, tile_mappings)
    screentext.draw(screen)
    

    pygame.display.update()
    clock.tick(60)
    