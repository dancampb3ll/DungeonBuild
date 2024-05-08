import pygame
import overworldTiles

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
TILE_SIZE = 16
TILE_COUNT = SCREEN_HEIGHT / TILE_SIZE
PLAYERSPEED = 2
CAMERASPEED = PLAYERSPEED
WALKABLE_TILES = overworldTiles.WALKABLE


LIGHT_BLUE = (173, 216, 230)

#A tile is initialised with a gridx and gridy location. The true x and true y are then multiples of these by the tile size.
class OutdoorTile(pygame.sprite.Sprite):
    def __init__(self, gridx, gridy, tiletypename, pygame_group):
        super().__init__(pygame_group)
        self.type = "tile"
        self.tile = tiletypename
        self.ignorecolour = (255, 128, 255) #The pink colour on image backgrounds to be transparent
        self.image = pygame.image.load(f"assets/{self.tile}.png").convert()
        self.image.set_colorkey(self.ignorecolour)
        self.rect = self.image.get_rect()
        self.gridx = gridx
        self.gridy = gridy
        self.rect.x = gridx * TILE_SIZE
        self.rect.y = gridy * TILE_SIZE
        self.original_image = self.image.copy() #Required in case of image modifications (such as highlight for build)


    def update(self):
        None   

class Player(pygame.sprite.Sprite):
    def __init__(self, pygame_group):
        super().__init__(pygame_group)
        self.type = "player"
        self.image = pygame.image.load("assets/player.png").convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT // 2
        self.speed = PLAYERSPEED
        self.debug = ""
        self.buildmode = False
        self.B_key_down = False

    def detect_tile_collisions(self, camera_group, xspeed, yspeed):
        collide_count = 0
        for sprite in camera_group:
            if sprite.type == "tile":
                collide = sprite.rect.colliderect(self.rect)
                if collide:
                    collide_count += 0
                    if sprite.tile not in WALKABLE_TILES:
                        if xspeed > 0:
                            self.rect.right = sprite.rect.left
                        elif xspeed < 0:
                            self.rect.left = sprite.rect.right
                        if yspeed > 0:
                            self.rect.bottom = sprite.rect.top
                        elif yspeed < 0:
                            self.rect.top = sprite.rect.bottom

    def move_player(self, camera_group):
        if self.buildmode:
            return
        key = pygame.key.get_pressed()
        
        #Detection for diagonal speed reduction. 
        vertical = False
        horizontal = False
        if key[pygame.K_w] or key[pygame.K_s]:
            vertical = True
        if key[pygame.K_a] or key[pygame.K_d]:
            horizontal = True
        if vertical and horizontal:
            #Multiply speed by the inverse of sqrt of 2 if moving diagonally
            self.speed = PLAYERSPEED * 0.707
        else:
            self.speed = PLAYERSPEED

        #left
        if key[pygame.K_a]:
            self.rect.x -= self.speed
            self.detect_tile_collisions(camera_group, -self.speed, 0)
        #right
        elif key[pygame.K_d]:
            self.rect.x += self.speed
            self.detect_tile_collisions(camera_group, self.speed, 0)
        #down
        if key[pygame.K_s]:
            self.rect.y += self.speed
            self.detect_tile_collisions(camera_group, 0, self.speed)
        #up
        elif key[pygame.K_w]:
            self.rect.y -= self.speed
            self.detect_tile_collisions(camera_group, 0, -self.speed)

    def check_build_mode(self, input_events, buildhud, camera_group):
        for event in input_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b and not self.B_key_down:
                    self.toggle_build_mode(buildhud, camera_group)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_b:
                    self.B_key_down = False

    def toggle_build_mode(self, buildhud, camera_group):
        if self.buildmode == False:
            self.buildmode = True
            buildhud.show()
        else:
            self.buildmode = False
            buildhud.hide()
            self.reset_tile_highlights(camera_group)

    
    def reset_tile_highlights(self, camera_group):
        for sprite in camera_group.sprites():
            if sprite.type == "tile":
                sprite.image = sprite.original_image.copy()

    def place_building_get_coords(self, input_events, camera_group):
        """Highlights tiles in build mode and returns clicked tiles.
        """
        if not self.buildmode:
            return None
        gridx = 0
        gridy = 0
        top_left_highlighted_sprite = None #Used for hovering in build mode to show the player where the object will be placed. Need to work on this.
        for event in input_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for sprite in camera_group:
                    if sprite.type == "tile":
                        raw_mouse_pos = event.pos
                        offset_adjusted_mouse_pos = (raw_mouse_pos[0] + camera_group.offset.x, raw_mouse_pos[1] + camera_group.offset.y)
                        if sprite.rect.collidepoint(offset_adjusted_mouse_pos):
                            gridx = sprite.gridx
                            gridy = sprite.gridy

            elif event.type == pygame.MOUSEMOTION:
                top_left_highlighted_sprite = None
                for sprite in camera_group:
                    if sprite.type == "tile":
                        raw_mouse_pos = event.pos
                        offset_adjusted_mouse_pos = (raw_mouse_pos[0] + camera_group.offset.x, raw_mouse_pos[1] + camera_group.offset.y)
                        if sprite.rect.collidepoint(offset_adjusted_mouse_pos):
                            top_left_highlighted_sprite = sprite
                            sprite.image.fill(LIGHT_BLUE, special_flags=pygame.BLEND_ADD)
                        else:
                            sprite.image = sprite.original_image.copy()

        if top_left_highlighted_sprite is None:
            for sprite in camera_group:
                if sprite.type == "tile":
                    sprite.image = sprite.original_image.copy()

        gridcoords = (gridx, gridy)
        return gridcoords

    def update(self):
        None
        #print((self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE))
        #debug = f"self.rect.center {self.rect.center} | self.rect.bottomleft {self.rect.bottomleft} | self.rect.topright {self.rect.topright} | self.rect.center tile {self.rect.center[0] // (TILE_SIZE)} | self.rect.bottomleft tile {self.rect.bottomleft[0] // TILE_SIZE} | self.rect.topright tile {self.rect.topright[0] // TILE_SIZE}"
        #if debug != self.debug:
        #    self.debug = debug
        #    print(self.debug)

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

class FloatingHud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = "hud"
        self.image = pygame.image.load("assets/hud/hudbar.png").convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH - self.rect.w
        self.rect.y = SCREEN_HEIGHT - self.rect.h

class BuildHud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/hud/buildhudbar.png").convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.x = 2*SCREEN_WIDTH
        self.rect.y = 100
        
    def show(self):
        self.rect.x = SCREEN_WIDTH - self.rect.w

    def hide(self):
        #There must be a better way to do this
        self.rect.x = 2*SCREEN_WIDTH

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


pygame.init()
 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('DungeonBuild')

#Camera must be defined first
cameragroup = CameraGroup()

hud = pygame.sprite.Group()
hudbar = FloatingHud()
cointext = CoinText(hudbar.rect.topleft[0], hudbar.rect.topleft[1])
buildhud = BuildHud()
hud.add(hudbar)
hud.add(cointext)
hud.add(buildhud)

#Drawing tiles
#debug grid
debuggrid = False
if debuggrid:
    for i in range(0, 40):
        for j in range(0, 40):
            OutdoorTile(i, j, "overgroundGrid", cameragroup)

overworldmapdict = overworldTiles.overworldmapdict
tile_mappings = overworldTiles.TILE_MAPPINGS


#overworldmapdict = overworldTiles.detect_building_worldmap_collision_place_and_changes(overworldmapdict, "smallDungeon", (23, 23))[0]

#Used to maintain sprites at given locations.
spriteDict = {}

#Map initialisation - creates sprites for tiles that aren't blanks (value 0)
for coord in overworldmapdict.keys():
    x = coord[0]
    y = coord[1]
    tiletype = overworldmapdict[(x, y)]
    if tiletype != 0:
        tilename = tile_mappings[tiletype]
        spriteDict[(x, y)] = OutdoorTile(x, y, tilename, cameragroup)

def build_and_perform_tile_sprite_updates(mapdict, structuretype, topleftplacementcoord: tuple):
    """Gets the world map, looks where the structure is to be built, and if possible deletes sprites from the spritedict.
    Returns the new world map.
    """
    if topleftplacementcoord == None:
        return mapdict
    newmap, changes = overworldTiles.detect_building_worldmap_collision_place_and_changes(mapdict, structuretype, topleftplacementcoord)
    if changes == None:
        return mapdict
    #A change is given in format [(x,y), tilenum]
    for change in changes:
        x = change[0][0]
        y = change[0][1]
        tilenum = change[1]
        tilename = tile_mappings[tilenum]
        spriteDict[(change[0][0], change[0][1])].kill()
        spriteDict[(change[0][0], change[0][1])] = OutdoorTile(x, y, tilename, cameragroup)
    return newmap

overworldmapdict = build_and_perform_tile_sprite_updates(overworldmapdict, "smallDungeon", (23, 23))


player = Player(cameragroup)

debugtext = DebugText()
screentext = pygame.sprite.Group()
screentext.add(debugtext)

running = True
while running:
    input_events = pygame.event.get()
    for event in input_events:
        if event.type == pygame.QUIT:
            running = False

    screen.fill((10, 10, 18))

    #Cameragroup contains tile sprites, which are used to detect collisions.
    player.move_player(cameragroup)
    player.check_build_mode(input_events, buildhud, cameragroup)
    
    player_placement_coords_topleft = player.place_building_get_coords(input_events, cameragroup)
    build_and_perform_tile_sprite_updates(overworldmapdict, "smallDungeon", player_placement_coords_topleft)

    cameragroup.update()
    cameragroup.custom_draw(player)

    debugtext.update(round(player.rect.x / TILE_SIZE), round(player.rect.y / TILE_SIZE), overworldmapdict, tile_mappings)
    screentext.draw(screen)

    hud.draw(screen)

    pygame.display.update()
    clock.tick(60)
    