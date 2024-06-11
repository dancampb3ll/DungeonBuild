import math
import pygame
import underworld.tiles
import settings
import random

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
        self.rect = self.image.get_rect()
        self.gridx = 1
        self.gridy = 1
        self.rect.x = self.gridx * settings.UNDERWORLD_TILE_SIZE
        self.rect.y = self.gridy * settings.UNDERWORLD_TILE_SIZE
        self.health = 100
        self.speed = UNDERWORLD_PLAYERSPEED
        self.coins_collected = 0

        self.gameworld = "underworld"

        self.invincibility_state = False
        self.invincibility_timer = 0
        self.INVINCIBILITY_MAX_TIME = 20

        #Used in view bobbing
        self.is_moving = False
        self.is_moving_x = False
        self.is_moving_y = False
        
        self.knockbackx = None
        self.knockbacky = None
        #Used to stop an enemy being stuck for too long.
        self.knockback_timer = 0
        self.KNOCKBACK_TIMER_MAX = 80

    def detect_tile_collisions(self, camera_group, xspeed, yspeed):
        for sprite in camera_group:
            if sprite.type == "tile":
                collide = sprite.rect.colliderect(self.rect)
                if collide:
                    if sprite.tile not in underworld.tiles.WALKABLE:
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

    def update_invincibility_state(self):
        if not self.invincibility_state:
            return
        self.invincibility_timer += 1
        if self.invincibility_timer > self.INVINCIBILITY_MAX_TIME:
            self.invincibility_timer
            self.invincibility_state = False


    def take_damage(self, npc):
        if self.invincibility_state:
            print("invincible")
            return
        self.health -= npc.damage
        print("damage taken")
        self.invincibility_state = True
        self.invincibility_timer = 0
        
        ##Audit
        self.set_knockback_position(npc.direction, npc.knockback)

    def set_knockback_position(self, enemy_direction, enemy_knockback):
        npc_knockback = enemy_knockback
        knockback_effect = npc_knockback
        if enemy_direction == "left":
            self.knockbackx = self.rect.x - knockback_effect
        elif enemy_direction == "right":
            self.knockbackx = self.rect.x + knockback_effect
        elif enemy_direction == "up":
            self.knockbacky = self.rect.y - knockback_effect
        elif enemy_direction == "down":
            self.knockbacky = self.rect.y + knockback_effect

    def perform_knockback(self, camera):
        if self.knockbackx == None and self.knockbacky == None:
            self.knockback_timer = 0
            return
        
        self.knockback_timer += 1
        if self.knockback_timer > self.KNOCKBACK_TIMER_MAX:
            self.knockbackx = None
            self.knockbacky = None
            return

        knockback_speed = settings.KNOCKBACK_SPEED

        if self.knockbackx != None:
            if self.knockbackx > self.rect.x:
                self.rect.x = min(self.knockbackx, self.rect.x + knockback_speed)
                if self.rect.x != self.knockbackx:
                    self.detect_tile_collisions(camera, knockback_speed, 0)
            elif self.knockbackx < self.rect.x:
                self.rect.x = max(self.knockbackx, self.rect.x - knockback_speed)
                if self.rect.x != self.knockbackx:
                    self.detect_tile_collisions(camera, -knockback_speed, 0)
            else:
                self.knockbackx = None

        if self.knockbacky != None:
            if self.knockbacky > self.rect.y:
                self.rect.y = min(self.knockbacky, self.rect.y + knockback_speed)
                if self.rect.y != self.knockbacky:
                    self.detect_tile_collisions(camera, 0, knockback_speed)
            elif self.knockbacky < self.rect.y:
                self.rect.y = max(self.knockbacky, self.rect.y - knockback_speed)
                if self.rect.y != self.knockbacky:
                    self.detect_tile_collisions(camera, 0, -knockback_speed)
            else:
                self.knockbacky = None

    def move_player(self, camera_group):
        self.is_moving = False #Used to check if player is walking
        self.is_moving_x = False
        self.is_moving_y = False
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
            speed = UNDERWORLD_PLAYERSPEED * 0.707
        else:
            speed = UNDERWORLD_PLAYERSPEED

        #left
        if key[pygame.K_a]:
            self.facing_direction = "left"
            self.rect.x -= speed
            self.detect_tile_collisions(camera_group, -speed, 0)
            self.is_moving = True
            self.is_moving_x = True
        #right
        elif key[pygame.K_d]:
            self.facing_direction = "right"
            self.rect.x += speed
            self.detect_tile_collisions(camera_group, speed, 0)
            self.is_moving = True
            self.is_moving_x = True
        #down
        if key[pygame.K_s]:
            self.facing_direction = "down"
            self.rect.y += speed
            self.detect_tile_collisions(camera_group, 0, speed)
            self.is_moving = True
            self.is_moving_y = True
        #up
        elif key[pygame.K_w]:
            self.facing_direction = "up"
            self.rect.y -= speed
            self.detect_tile_collisions(camera_group, 0, -speed)
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

    def update_death_status(self):
        if self.health <= 0:
            self.gameworld = "overworld"

    def custom_update(self, camera):
        self.update_invincibility_state()
        self.perform_knockback(camera)
        self.update_grid_locations()
        self.update_player_image_from_direction_and_aniframe()
        self.update_death_status()

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
        self.attributes = {
            "dagger": {
                "attack_width": 40,
                "attack_length": 33,
                "attack_duration": 10,
                "sfx": ["sword1.mp3", "sword2.mp3", "sword3.mp3"],
                "damage": 1,
                "knockback": 80
            }
        }
        self.attack_width = self.attributes[self.weapon]["attack_width"]
        self.attack_length = self.attributes[self.weapon]["attack_length"]
        self.attack_duration = self.attributes[self.weapon]["attack_duration"]
        self.sfx = self.attributes[self.weapon]["sfx"]
        self.damage = self.attributes[self.weapon]["damage"]
        self.knockback = self.attributes[self.weapon]["knockback"]

        self.is_attacking = True
        self.attack_timer = 99999
        self.hitbox_rect = None
        self.DEBUG_DRAW_HITBOXES = settings.DEBUG_DRAW_HITBOXES

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