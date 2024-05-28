import math
import pygame
import underworld.tiles
import settings

WALKABLE_TILES = underworld.tiles.WALKABLE
UNDERWORLD_PLAYERSPEED = 3
LIGHT_BLUE = (173, 216, 230)

class Player(pygame.sprite.Sprite):
    def __init__(self, pygame_group):
        super().__init__(pygame_group)
        self.type = "player"
        self.facing_direction = "down"
        self.aniframe = 1
        self.ANIFRAME_COUNT = 4
        self.ANIFRAME_TIME_LIMIT = 10
        self.aniframe_time_count = 0
        self.image = pygame.image.load(f"assets/player/underworld/{self.facing_direction}{self.aniframe}.png").convert_alpha()
        #self.image = pygame.image.load(f"assets/player/underworld/player.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = 2 * settings.UNDERWORLD_TILE_SIZE
        self.rect.y = 2 * settings.UNDERWORLD_TILE_SIZE
        self.gridx = round(self.rect.x / settings.UNDERWORLD_TILE_SIZE)
        self.gridy = round(self.rect.y / settings.UNDERWORLD_TILE_SIZE)
        self.speed = UNDERWORLD_PLAYERSPEED
        self.B_key_down = False
        self.top_left_highlighted_sprite = None

        self.gameworld = "overworld"

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
    
    def detect_void_collision(self, camera_group, xspeed, yspeed):
        collideleft = False
        collidetop = False
        collideright = False
        collidebottom = False
        for sprite in camera_group:
            if sprite.type == "tile":
                if sprite.tile in underworld.tiles.WALKABLE:
                    if sprite.rect.collidepoint(self.rect.midleft):
                        collideleft = True
                    if sprite.rect.collidepoint(self.rect.midtop):
                        collidetop = True
                    if sprite.rect.collidepoint(self.rect.midright):
                        collideright = True
                    if sprite.rect.collidepoint(self.rect.midbottom):
                        collidebottom = True
        if collideleft == False:
            self.rect.x += xspeed
        if collidetop == False:
            self.rect.y += yspeed
        if collideright == False:
            self.rect.x -= xspeed
        if collidebottom == False:
            self.rect.y -= yspeed


    def move_player(self, camera_group):
        direction_pressed = False #Used to check if player is walking
        key = pygame.key.get_pressed()
        
        #Detection for diagonal speed reduction. 
        vertical = False
        horizontal = False
        self.detect_void_collision(camera_group, UNDERWORLD_PLAYERSPEED, UNDERWORLD_PLAYERSPEED)
        if key[pygame.K_w] or key[pygame.K_s]:
            vertical = True
        if key[pygame.K_a] or key[pygame.K_d]:
            horizontal = True
        if vertical and horizontal:
            #Multiply speed by the inverse of sqrt of 2 if moving diagonally
            self.speed = UNDERWORLD_PLAYERSPEED * 0.707
        else:
            self.speed = UNDERWORLD_PLAYERSPEED

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
            self.aniframe_time_count = 0
        if self.aniframe_time_count > self.ANIFRAME_TIME_LIMIT:
            if self.aniframe == self.ANIFRAME_COUNT:
                self.aniframe = 1
                self.aniframe_time_count = 0
            else:
                self.aniframe += 1
                self.aniframe_time_count = 0

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
        self.image = pygame.image.load(f"assets/player/underworld/{self.facing_direction}{self.aniframe}.png").convert_alpha()
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

    def custom_update(self):
        self.update_grid_locations()
        self.update_player_image_from_direction_and_aniframe()

class Weapon(pygame.sprite.Sprite):
    def __init__(self, pygame_group, weapon_name):
        super().__init__(pygame_group)
        self.type = "weapon"
        self.weapon = weapon_name
        self.ignorecolour = (255, 0, 255)
        self.rect = None
        self.image = None
        self.weapon_offsets = { #Given in (xoffset, yoffset) format
            "dagger": (5, 5)
        }

    def update_weapon_position(self, player_rect, player_direction):
        self.image = pygame.image.load(f"assets/player/underworld/weapons/{self.weapon}/{player_direction}.png").convert()
        self.image.set_colorkey(self.ignorecolour)
        self.rect = self.image.get_rect()
        if player_direction == "down":
            xoffset = -self.weapon_offsets[self.weapon][0]
            yoffset = 0
            player_coords = player_rect.midleft
        elif player_direction == "left":
            xoffset = 0
            yoffset = -self.weapon_offsets[self.weapon][1]
            player_coords = player_rect.midtop
        elif player_direction == "right":
            xoffset = 0
            yoffset = self.weapon_offsets[self.weapon][1]
            player_coords = player_rect.midbottom
        elif player_direction == "up":
            xoffset = self.weapon_offsets[self.weapon][0]
            yoffset = 0
            player_coords = player_rect.midright
        self.rect.x = player_coords[0] + xoffset
        self.rect.y = player_coords[1] + yoffset