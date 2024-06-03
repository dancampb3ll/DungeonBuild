import math
import pygame
import underworld.tiles
import settings
import random

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
        self.is_moving = False
        self.is_moving_x = False
        self.is_moving_y = False
        self.gameworld = "underworld"

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
        self.is_moving = False #Used to check if player is walking
        self.is_moving_x = False
        self.is_moving_y = False
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
            self.is_moving = True
            self.is_moving_x = True
        #right
        elif key[pygame.K_d]:
            self.facing_direction = "right"
            self.rect.x += self.speed
            self.detect_tile_collisions(camera_group, self.speed, 0)
            self.is_moving = True
            self.is_moving_x = True
        #down
        if key[pygame.K_s]:
            self.facing_direction = "down"
            self.rect.y += self.speed
            self.detect_tile_collisions(camera_group, 0, self.speed)
            self.is_moving = True
            self.is_moving_y = True
        #up
        elif key[pygame.K_w]:
            self.facing_direction = "up"
            self.rect.y -= self.speed
            self.detect_tile_collisions(camera_group, 0, -self.speed)
            self.is_moving = True
            self.is_moving_y = True
        
        #Changes the frame to the next frame in the current direction.
        # If direction pressed, add to counter
        if self.is_moving:
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
            "dagger": {
                "up": (-5, -5),
                "down": (-8, -5),
                "left": (-18, 9),
                "right": (2, -10)
            }
        }
        self.weapon_attributes = {
            "dagger": {
                "attack_width": 40,
                "attack_length": 33,
                "attack_duration": 10,
                "sfx": ["sword1.mp3", "sword2.mp3", "sword3.mp3"],
                "damage": 1,
                "knockback": 80
            }
        }
        self.attack_width = self.weapon_attributes[self.weapon]["attack_width"]
        self.attack_length = self.weapon_attributes[self.weapon]["attack_length"]
        self.attack_duration = self.weapon_attributes[self.weapon]["attack_duration"]
        self.sfx = self.weapon_attributes[self.weapon]["sfx"]
        self.damage = self.weapon_attributes[self.weapon]["damage"]
        self.knockback = self.weapon_attributes[self.weapon]["knockback"]

        self.is_attacking = True
        self.attack_timer = 99999
        self.hitbox_rect = None
        self.DEBUG_DRAW_HITBOXES = True

        #Bobbing calcs
        self.player_is_moving_x = False
        self.bobbing_amplitude_x = 1.6
        self.bobbing_speed_x = 0.4
        self.bobbing_count_x = 0
        self.player_is_moving_y = False
        self.bobbing_amplitude_y = 1
        self.bobbing_speed_y = 0.4
        self.bobbing_count_y = 0
        #****************************
        self.player_direction = None

    def get_bobbing_offset_x(self, player_is_moving_x):
        if player_is_moving_x:
            self.bobbing_count_x += self.bobbing_speed_x
        else:
            self.bobbing_count_x = 0
        bobbing_offset_x = self.bobbing_amplitude_x * math.sin(self.bobbing_count_x)
        return bobbing_offset_x
    
    def get_bobbing_offset_y(self, player_is_moving_y):
        if player_is_moving_y:
            self.bobbing_count_y += self.bobbing_speed_y
        else:
            self.bobbing_count_y = 0
        bobbing_offset_y = self.bobbing_amplitude_y * math.sin(self.bobbing_count_y)
        return bobbing_offset_y

    def update_weapon_position(self, player_rect, player_direction, player_is_moving_x, player_is_moving_y):
        self.image = pygame.image.load(f"assets/player/underworld/weapons/{self.weapon}/{player_direction}.png").convert()
        self.image.set_colorkey(self.ignorecolour)
        self.rect = self.image.get_rect()
        if player_direction == "down":
            player_coords = player_rect.midleft
        elif player_direction == "left":
            player_coords = player_rect.midtop
        elif player_direction == "right":
            player_coords = player_rect.midbottom
        elif player_direction == "up":
            player_coords = player_rect.midright
        xoffset = self.weapon_offsets[self.weapon][player_direction][0]
        yoffset = self.weapon_offsets[self.weapon][player_direction][1]
        self.rect.x = player_coords[0] + xoffset + self.get_bobbing_offset_x(player_is_moving_x)
        self.rect.y = player_coords[1] + yoffset + self.get_bobbing_offset_y(player_is_moving_y)

    def update_attack_hitbox_and_detect_collisions(self, screen, camera_group, player_rect, player_direction, input_events):
        self.player_direction = player_direction
        if self.is_attacking:
            if self.attack_timer < self.attack_duration:
                self.attack_timer += 1
                
                if self.player_direction == "up":
                    #Vertical rect
                    playerx = player_rect.center[0]
                    playery = player_rect.center[1]
                    hitbox_width = self.attack_width
                    hitbox_height = self.attack_length
                    x = playerx - 0.5*hitbox_width
                    y = playery - hitbox_height 
                elif self.player_direction == "down":
                    #Vertical rect
                    playerx = player_rect.center[0]
                    playery = player_rect.center[1]
                    hitbox_width = self.attack_width
                    hitbox_height = self.attack_length
                    x = playerx - 0.5*hitbox_width
                    y = playery
                elif self.player_direction == "left":
                    #Horizontal rect (width and length swapped)
                    playerx = player_rect.center[0]
                    playery = player_rect.center[1]
                    hitbox_width = self.attack_length
                    hitbox_height = self.attack_width
                    x = playerx - hitbox_width
                    y = playery - 0.5*hitbox_height
                elif self.player_direction == "right":
                    #Horizontal rect (width and length swapped)
                    playerx = player_rect.center[0]
                    playery = player_rect.center[1]
                    hitbox_width = self.attack_length
                    hitbox_height = self.attack_width
                    x = playerx
                    y = playery - 0.5*hitbox_height
                

                self.hitbox_rect = pygame.Rect(x, y, hitbox_width, hitbox_height)
                self.show_hitboxes_debug(screen, camera_group)
            else:
                self.attack_timer = 0
                self.is_attacking = False
                self.hitbox_rect = None
        else:
            for event in input_events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.is_attacking = True
                        sfx_list = self.sfx
                        random_sfx_num = random.randint(0, len(sfx_list) - 1)
                        sfx = pygame.mixer.Sound(f"assets/sfx/weapons/{sfx_list[random_sfx_num]}")
                        sfx.play()

    def show_hitboxes_debug(self, screen, camera_group):
        if self.DEBUG_DRAW_HITBOXES:
            offset_hitbox = self.hitbox_rect.move(-camera_group.offset[0], -camera_group.offset[1])
            pygame.draw.rect(screen, (255, 0, 0), offset_hitbox, 1)

    def detect_enemy_weapon_collision(self, camera_group):
        if self.hitbox_rect == None:
            return
        for sprite in camera_group:
            if sprite.type == "npc":
                if self.hitbox_rect.colliderect(sprite.rect):
                    sprite.take_damage(self)

    def melee_swipe_movement(self):
        None