import pygame
import overworldTiles
import overworldBuildings
import math

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
TILE_SIZE = 16
TILE_COUNT = SCREEN_HEIGHT / TILE_SIZE
PLAYERSPEED = 2
CAMERASPEED = PLAYERSPEED
WALKABLE_TILES = overworldTiles.WALKABLE
BUILDING_TYPES = overworldBuildings.BUILDING_TYPES

LIGHT_BLUE = (173, 216, 230)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('DungeonBuild')
pygame.init()

#Later to be modularised
pygame.mixer.init()
pygame.mixer.music.load("assets/music/overworld/Lost-Jungle.mp3")
pygame.mixer.music.play(-1) #Repeat unlimited
grass_sfx = pygame.mixer.Sound("assets/sfx/GrassPlacement.mp3")
building_sfx = pygame.mixer.Sound("assets/sfx/BuildingPlacement.mp3")

#A tile is initialised with a gridx and gridy location. The true x and true y are then multiples of these by the tile size.
class OutdoorTile(pygame.sprite.Sprite):
    def __init__(self, gridx, gridy, tiletypename, pygame_group):
        super().__init__(pygame_group)
        self.type = "tile"
        self.tile = tiletypename
        self.ignorecolour = (255, 128, 255) #The pink colour on image backgrounds to be transparent
        if self.tile == "overgroundBorder":
            self.ignorecolour = (0, 0, 0)
        
        self.image = pygame.image.load(f"assets/{self.tile}.png").convert()
        self.raw_image = self.image.copy() #Required in case of image modifications (such as highlight for build)
        self.image.set_colorkey(self.ignorecolour)
        self.rect = self.image.get_rect()
        self.gridx = gridx
        self.gridy = gridy
        self.rect.x = gridx * TILE_SIZE
        self.rect.y = gridy * TILE_SIZE

    def update(self):
        None
        #self.image.set_colorkey(self.ignorecolour)

class Player(pygame.sprite.Sprite):
    def __init__(self, pygame_group):
        super().__init__(pygame_group)
        self.type = "player"
        self.image = pygame.image.load("assets/player.png").convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT // 2
        self.gridx = round(self.rect.x / TILE_SIZE)
        self.gridy = round(self.rect.y / TILE_SIZE)
        self.speed = PLAYERSPEED
        self.debug = ""
        self.buildmode = False
        self.B_key_down = False
        self.top_left_highlighted_sprite = None
        self.right_mouse_button_held = False
        self.selected_building_index = 0
        self.selected_building = BUILDING_TYPES[self.selected_building_index]

    def adjust_selected_building(self, input_events, left_tooltip_instance):
        #Left tooltip is needed as an object to a
        if not self.buildmode:
            return
        UPWARD_SCROLL = 1
        DOWNWARD_SCROLL = -1
        for event in input_events:
             if event.type == pygame.MOUSEWHEEL:
                if event.y == UPWARD_SCROLL:
                    if self.selected_building_index == len(BUILDING_TYPES) - 1:
                        self.selected_building_index = 0
                    else:
                        self.selected_building_index += 1
                elif event.y == DOWNWARD_SCROLL:
                    if self.selected_building_index == 0:
                        self.selected_building_index = len(BUILDING_TYPES) - 1
                    else:
                        self.selected_building_index -= 1
        self.selected_building = BUILDING_TYPES[self.selected_building_index]
        if left_tooltip_instance:
            left_tooltip_instance.building_type = self.selected_building

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

    def toggle_border_alpha(self, camera_group, buildmode):
        """Stops the background border colour from being black to make it slightly visible when in build mode.
        """
        for sprite in camera_group.sprites():
            if sprite.type == "tile":
                if sprite.tile == "overgroundBorder":
                    if buildmode:
                        sprite.image = sprite.raw_image
                        sprite.ignorecolour = (123, 123, 123) #This is a random colour
                        sprite.image.set_colorkey(sprite.ignorecolour)
                    else:
                        sprite.image = sprite.raw_image
                        sprite.ignorecolour = (0, 0, 0)
                        sprite.image.set_colorkey(sprite.ignorecolour)

    def toggle_build_mode(self, buildhud, camera_group):
        if self.buildmode == False:
            self.buildmode = True
            self.toggle_border_alpha(camera_group, self.buildmode)
            buildhud.show()
        else:
            self.buildmode = False
            self.toggle_border_alpha(camera_group, self.buildmode)
            buildhud.hide()
            self.reset_tile_highlights(camera_group)

    def reset_tile_highlights(self, camera_group):
        for sprite in camera_group.sprites():
            if sprite.type == "tile":
                sprite.image = sprite.raw_image.copy()

    def place_building_get_coords(self, input_events, camera_group):
        """Highlights tiles in build mode and returns positions of clicked tiles in (gridx, gridy) tuple format.\n
        Requires the camera group to offset mouse detection.\n
        """
        if not self.buildmode:
            return None
        gridx = 0
        gridy = 0
        #Highlighted sprite is needed to unhighlight a cell if the mouse scrolls off the tile.
        for event in input_events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for sprite in camera_group:
                    if sprite.type == "tile":
                        raw_mouse_pos = event.pos
                        offset_adjusted_mouse_pos = (raw_mouse_pos[0] + camera_group.offset.x, raw_mouse_pos[1] + camera_group.offset.y)
                        if sprite.rect.collidepoint(offset_adjusted_mouse_pos):
                            gridx = sprite.gridx
                            gridy = sprite.gridy

            elif event.type == pygame.MOUSEMOTION:
                for sprite in camera_group:
                    if sprite.type == "tile":
                        raw_mouse_pos = event.pos
                        offset_adjusted_mouse_pos = (raw_mouse_pos[0] + camera_group.offset.x, raw_mouse_pos[1] + camera_group.offset.y)
                        if sprite.rect.collidepoint(offset_adjusted_mouse_pos):
                            new_top_left_highlighted_sprite = (sprite.gridx, sprite.gridy)
                            if new_top_left_highlighted_sprite != self.top_left_highlighted_sprite:
                                sprite.image.fill(LIGHT_BLUE, special_flags=pygame.BLEND_ADD)
                                self.top_left_highlighted_sprite = new_top_left_highlighted_sprite

            for sprite in camera_group:
                if sprite.type == "tile":
                    if (sprite.gridx, sprite.gridy) != self.top_left_highlighted_sprite: 
                        sprite.image = sprite.raw_image.copy()

        if (gridx, gridy) == (0, 0):
            return None
        
        topleft_placement_coords = (gridx, gridy)
        return topleft_placement_coords

    def place_grass_block_get_coords(self, input_events, camera_group):
        if not self.buildmode:
            return None
        placement_coords = None

        for event in input_events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.right_mouse_button_held = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                self.right_mouse_button_held = False

            if self.right_mouse_button_held:
                raw_mouse_pos = pygame.mouse.get_pos()
                offset_adjusted_mouse_pos = (raw_mouse_pos[0] + camera_group.offset.x, raw_mouse_pos[1] + camera_group.offset.y)
                placement_coords = (offset_adjusted_mouse_pos[0] // TILE_SIZE, offset_adjusted_mouse_pos[1] // TILE_SIZE)
        
        if placement_coords is None:
            return None

        return placement_coords

    def update_grid_locations(self):
        """
        Used to update the gridx and gridy locations of the player based on the current x and y values of the rect.
        """
        self.gridx = round(self.rect.x / TILE_SIZE)
        self.gridy = round(self.rect.y / TILE_SIZE)

    def get_player_corner_grid_locations(self):
        topleft = self.rect.topleft
        topright = self.rect.topright
        bottomleft = self.rect.bottomleft
        bottomright = self.rect.bottomright
        rawcoords = [topleft, topright, bottomleft, bottomright]
        gridcoords = []
        for rawcoord in rawcoords:
            #Need to round up and round down so that any overlap pixels get accounted for.
            gridcoord_rounddown = []
            gridcoord_roundup = []
            for raw_single_coord in rawcoord:
                gridcoord_rounddown.append(math.floor(raw_single_coord / TILE_SIZE))
                gridcoord_roundup.append(math.ceil(raw_single_coord / TILE_SIZE))
            gridcoords.append(tuple(gridcoord_rounddown))
            gridcoords.append(tuple(gridcoord_roundup))
        return gridcoords

    def custom_update(self, input_events, left_tooltip_instance):
        self.adjust_selected_building(input_events, left_tooltip_instance)
        self.update_grid_locations()

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

def build_and_perform_tile_sprite_updates(mapdict, structuretype, topleftplacementcoord: tuple, player_corner_gridcoords_list):
    """Gets the world map, looks where the structure is to be built, and if possible deletes sprites from the spritedict.
    Returns the new world map dict with new buildings as replacements for old.
    """
    if topleftplacementcoord == None:
        return mapdict

    newmap, changes = overworldTiles.detect_building_worldmap_collision_place_and_changes(mapdict, structuretype, topleftplacementcoord, player_corner_gridcoords_list)
    if changes == None:
        return mapdict
    #A change is given in format [(x,y), tilenum]
    for change in changes:
        x = change[0][0]
        y = change[0][1]
        tilenum = change[1]
        tilename = tile_mappings[tilenum]
        #Kills the original sprite before generating a new tile to replace it.
        spriteDict[(x, y)].kill()
        #Creates an instance of the new tile.
        spriteDict[(x, y)] = OutdoorTile(x, y, tilename, cameragroup)
    building_sfx.play()
    return newmap

def draw_new_border_tiles_from_grass_placement(mapdict, placementx, placementy):
    for adjacentoffset in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
        checkx = placementx + adjacentoffset[0]
        checky = placementy + adjacentoffset[1]

        check_sprite = spriteDict.get((checkx, checky), None)
        if check_sprite is None:
            spriteDict[(checkx, checky)] = OutdoorTile(checkx, checky, "overgroundBorder", cameragroup)
            mapdict[(checkx, checky)] = 4

def build_grass_block_and_perform_tile_sprite_updates(mapdict, placementcoord):
    if placementcoord is None:
        return mapdict
    x = placementcoord[0]
    y = placementcoord[1]
    tile_sprite = spriteDict.get((x,y), None)
    if tile_sprite is None:
        return mapdict
    if tile_sprite.tile != "overgroundBorder":
        return mapdict
    spriteDict[(x, y)].kill()
    spriteDict[(x, y)] = OutdoorTile(x, y, "overgroundGrass", cameragroup)
    draw_new_border_tiles_from_grass_placement(mapdict, x, y)
    grass_sfx.play()
    mapdict[(x, y)] = 2

    return mapdict

def check_buildmode_and_update_tooltips(player_buildmode, player_selected_building, leftTT, rightTT, input_events):
    if not player_buildmode:
        for tooltip in building_tooltips:
            tooltip.kill()
        return None, None
    if len(building_tooltips) == 2:
        leftTT.update_tooltip_location_from_mouse(input_events)
        rightTT.update_tooltip_location_from_mouse(input_events)
        return leftTT, rightTT
    else:
        #Making new tooltips:
        leftTT = ToolTip(-999, -999, player_selected_building)
        rightTT = ToolTip(-999, -999, "overgroundGrass")
        building_tooltips.add(leftTT)
        building_tooltips.add(rightTT)
        return leftTT, rightTT

#Camera must be defined first
cameragroup = CameraGroup()

#HUD is separate from the camera
hud = pygame.sprite.Group()
hudbar = FloatingHud()
cointext = CoinText(hudbar.rect.topleft[0], hudbar.rect.topleft[1])
buildhud = BuildHud()
hud.add(hudbar)
hud.add(cointext)
hud.add(buildhud)

#Drawing tiles
overworldmapdict = overworldTiles.overworldmapdict
tile_mappings = overworldTiles.TILE_MAPPINGS

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

player = Player(cameragroup)

debugtext = DebugText()
screentext = pygame.sprite.Group()
screentext.add(debugtext)

building_tooltips = pygame.sprite.Group()
tooltip_left = None
tooltip_right = None

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
    player.custom_update(input_events, tooltip_left)

    #If none returned from get coords, nothing is changed on overworldmap dict
    player_building_placement_coords_topleft = player.place_building_get_coords(input_events, cameragroup)
    player_corner_coords_list = player.get_player_corner_grid_locations()
    overworldmapdict = build_and_perform_tile_sprite_updates(overworldmapdict, player.selected_building, player_building_placement_coords_topleft, player_corner_coords_list)

    #If none returned from get coords, nothing is changed on overworldmap dict
    player_Grass_placement_coords = player.place_grass_block_get_coords(input_events, cameragroup)
    overworldmapdict = build_grass_block_and_perform_tile_sprite_updates(overworldmapdict, player_Grass_placement_coords)

    cameragroup.remove(player)
    cameragroup.add(player)
    cameragroup.update()
    cameragroup.custom_draw(player)

    debugtext.update(player.gridx, player.gridy, overworldmapdict, tile_mappings)
    screentext.draw(screen)

    tooltip_left, tooltip_right = check_buildmode_and_update_tooltips(player.buildmode, player.selected_building, tooltip_left, tooltip_right, input_events) #Make largeHut dependent on player selected material

    hud.draw(screen)

    building_tooltips.update()
    building_tooltips.draw(screen)

    pygame.display.update()
    clock.tick(60)