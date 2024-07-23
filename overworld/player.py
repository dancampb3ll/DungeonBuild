import math
import pygame
import overworld.buildings
import overworld.tiles
import settings

WALKABLE_TILES = overworld.tiles.WALKABLE
PLAYERSPEED = 2
BUILDING_TYPES = overworld.buildings.BUILDING_TYPES
LIGHT_BLUE = (173, 216, 230)

def calculate_distance_pythagoras(point1: tuple, point2: tuple):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

class Player(pygame.sprite.Sprite):
    def __init__(self, pygame_group, gridx, gridy):
        super().__init__(pygame_group)
        self.type = "player"
        self.facing_direction = "down"
        self.aniframe = 1
        self.ANIFRAME_COUNT = 4
        self.ANIFRAME_TIME_LIMIT = 10
        self.aniframe_time_count = 0
        self.image = pygame.image.load(f"assets/player/overworld/{self.facing_direction}{self.aniframe}.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.gridx = gridx
        self.gridy = gridy
        self.rect.x = self.gridx * settings.OVERWORLD_TILE_SIZE
        self.rect.y = self.gridy * settings.OVERWORLD_TILE_SIZE
        self.speed = PLAYERSPEED
        self.debug = ""
        self.buildmode = False
        self.B_key_down = False
        self.top_left_highlighted_sprite = None
        self.right_mouse_button_held = False
        self.selected_building_index = 0
        self.selected_building = BUILDING_TYPES[self.selected_building_index]
        self.gameworld = "overworld"

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
        for sprite in camera_group:
            if sprite.type == "tile":
                collide = sprite.rect.colliderect(self.rect)
                if collide:
                    if sprite.tile not in WALKABLE_TILES:
                        if xspeed > 0:
                            self.rect.right = sprite.rect.left
                            self.check_portal_collisions("right", sprite)
                        elif xspeed < 0:
                            self.rect.left = sprite.rect.right
                            self.check_portal_collisions("left", sprite)
                        if yspeed > 0:
                            self.rect.bottom = sprite.rect.top
                            self.check_portal_collisions("bottom", sprite)
                        elif yspeed < 0:
                            self.rect.top = sprite.rect.bottom
                            self.check_portal_collisions("top", sprite)

    def move_player(self, camera_group):
        direction_pressed = False #Used to check if player is walking
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
            self.facing_direction = "left"
            self.rect.x -= self.speed
            self.detect_tile_collisions(camera_group, -self.speed, 0)
            direction_pressed = True
        #right
        elif key[pygame.K_d]:
            self.facing_direction = "right"
            self.rect.x += self.speed
            self.detect_tile_collisions(camera_group, self.speed, 0)
            direction_pressed = True
        #down
        if key[pygame.K_s]:
            self.facing_direction = "down"
            self.rect.y += self.speed
            self.detect_tile_collisions(camera_group, 0, self.speed)
            direction_pressed = True
        #up
        elif key[pygame.K_w]:
            self.facing_direction = "up"
            self.rect.y -= self.speed
            self.detect_tile_collisions(camera_group, 0, -self.speed)
            direction_pressed = True
        
        #Changes the frame to the next frame in the current direction.
        # If direction pressed, add to counter
        if direction_pressed:
            self.aniframe_time_count += 1
        #if nothing pressed, reset animation cycle and counter
        else:
            self.aniframe = 1
            self.aniframe_time_count = 9
        if self.aniframe_time_count > self.ANIFRAME_TIME_LIMIT:
            if self.aniframe == self.ANIFRAME_COUNT:
                self.aniframe = 1
                self.aniframe_time_count = 0
            else:
                self.aniframe += 1
                self.aniframe_time_count = 0

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
            self.right_mouse_button_held = False

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
                placement_coords = (int(offset_adjusted_mouse_pos[0] // settings.OVERWORLD_TILE_SIZE), int(offset_adjusted_mouse_pos[1] // settings.OVERWORLD_TILE_SIZE))
        
        if placement_coords is None:
            return None

        return placement_coords

    def update_grid_locations(self):
        """
        Used to update the gridx and gridy locations of the player based on the current x and y values of the rect.
        """
        self.gridx = round(self.rect.x / settings.OVERWORLD_TILE_SIZE)
        self.gridy = round(self.rect.y / settings.OVERWORLD_TILE_SIZE)

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
                gridcoord_rounddown.append(math.floor(raw_single_coord / settings.OVERWORLD_TILE_SIZE))
                gridcoord_roundup.append(math.ceil(raw_single_coord / settings.OVERWORLD_TILE_SIZE))
            gridcoords.append(tuple(gridcoord_rounddown))
            gridcoords.append(tuple(gridcoord_roundup))
        return gridcoords

    def update_player_image_from_direction_and_aniframe(self):
        self.image = pygame.image.load(f"assets/player/overworld/{self.facing_direction}{self.aniframe}.png").convert_alpha()
        #self.image.set_colorkey((255,255,251))

    def check_portal_collisions(self, player_collision_side, sprite):
        if sprite.portal_type == None:
            return

        complement_sides = {
            "bottom": "top",
            "top": "bottom",
            "left": "right",
            "right": "left"
        }
        if sprite.portal_type == "overworld":
            if complement_sides[player_collision_side] == sprite.portal_collision_side:
                self.rect.x = sprite.portal_destination[0] * settings.OVERWORLD_TILE_SIZE
                self.rect.y = sprite.portal_destination[1] * settings.OVERWORLD_TILE_SIZE
        self.gameworld = sprite.portal_type

    def custom_update(self, input_events, left_tooltip_instance):
        self.adjust_selected_building(input_events, left_tooltip_instance)
        self.update_grid_locations()
        self.update_player_image_from_direction_and_aniframe()

    def get_shop_window_shown_bool(self, shopkeeper_coords):
        result = False
        if calculate_distance_pythagoras(self.rect.center, shopkeeper_coords) < 40:
            result = True
        print(result)
        return result

    def update(self):
        None
        #print((self.rect.x // OVERWORLD_TILE_SIZE, self.rect.y // OVERWORLD_TILE_SIZE))
        #debug = f"self.rect.center {self.rect.center} | self.rect.bottomleft {self.rect.bottomleft} | self.rect.topright {self.rect.topright} | self.rect.center tile {self.rect.center[0] // (OVERWORLD_TILE_SIZE)} | self.rect.bottomleft tile {self.rect.bottomleft[0] // OVERWORLD_TILE_SIZE} | self.rect.topright tile {self.rect.topright[0] // OVERWORLD_TILE_SIZE}"
        #if debug != self.debug:
        #    self.debug = debug
        #    print(self.debug)