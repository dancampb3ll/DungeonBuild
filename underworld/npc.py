import pygame
import random
import math
import settings
import underworld

def calculate_distance_pythagoras(point1: tuple, point2: tuple):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

coin_group = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

class Npc(pygame.sprite.Sprite):
    def __init__(self, pygame_group, gridx, gridy, npctype):
        super().__init__(pygame_group)
        self.type = "npc"
        self.npc = npctype
        self.ignorecolour = (255, 0, 255)
        self.raw_image = pygame.image.load(f"assets/npc/underworld/{self.npc}.png").convert_alpha()
        self.image = self.raw_image.copy()

        self.rect = self.image.get_rect()
        self.gridx = gridx
        self.gridy = gridy
        self.rect.x = self.gridx * settings.UNDERWORLD_TILE_SIZE
        self.rect.y = self.gridy * settings.UNDERWORLD_TILE_SIZE
        self.direction = "right"
        self.randomid = random.randint(0, 99999)
        self.living = True
        
        self.projectile = None
        self.PROJECTILE_THROW_COOLDOWN_TIMER = 300
        self.projectile_timer = 0

        self.holding_projectile = False


        self.attributes = {
            "default": {
                "projectile_type": None
            },

            "slime": {
                "damage_sfx": ["take_damage1.mp3"],
                "death_sfx": ["death1.mp3"],
                "aggression_distance": 280,
                "knockback_resistance_min": 4,
                "knockback_resistance_max": 8,
                "speed_min" : 100,
                "speed_max" : 100,
                "health": 3,
                "damage": 5,
                "knockback": 20,
                "coindrop_min": 1,
                "coindrop_max": 4,
                "attack_type": "melee",
                "attack_range": 14,
                "animation_speed" : 50,
                "animation_frames_list": [1, 2]
            },

            "skeleton": {
                "damage_sfx": ["take_damage1.mp3"],
                "death_sfx": ["death1.mp3"],
                "aggression_distance": 280,
                "knockback_resistance_min": 4,
                "knockback_resistance_max": 8,
                "speed_min" : 200,
                "speed_max" : 200,
                "health": 7,
                "damage": 20,
                "knockback": 4,
                "coindrop_min": 4,
                "coindrop_max": 8,
                "attack_type": "ranged",
                "attack_range": 150,
                "animation_speed": 20,
                "animation_frames_list": [1, 2]
            }
        }
        self.health = self.attributes[self.npc]["health"]
        self.aggression_distance = self.attributes[self.npc]["aggression_distance"]
        self.damage_sfx = self.attributes[self.npc]["damage_sfx"]
        self.death_sfx = self.attributes[self.npc]["death_sfx"]
        self.knockback_resistance_min = self.attributes[self.npc]["knockback_resistance_min"]
        self.knockback_resistance_max = self.attributes[self.npc]["knockback_resistance_max"]
        self.knockback_resistance = random.randint(self.knockback_resistance_min, self.knockback_resistance_max)
        self.speed_min = self.attributes[self.npc]["speed_min"]
        self.speed_max = self.attributes[self.npc]["speed_max"]
        self.speed = random.randint(self.speed_min, self.speed_max) / 100
        self.damage = self.attributes[self.npc]["damage"]
        self.knockback = self.attributes[self.npc]["knockback"]
        self.coindrop_min = self.attributes[self.npc]["coindrop_min"]
        self.coindrop_max = self.attributes[self.npc]["coindrop_max"]
        self.coins_dropped = random.randint(self.coindrop_min, self.coindrop_max)
        self.attack_type = self.attributes[self.npc]["attack_type"]
        self.attack_range = self.attributes[self.npc]["attack_range"]
        self.projectile_type = self.attributes[self.npc].get("projectile_type", self.attributes["default"]["projectile_type"])
        

        self.knockbackx = None
        self.knockbacky = None
        
        #Used to stop an enemy being stuck for too long.
        self.knockback_timer = 0
        self.KNOCKBACK_TIMER_MAX = 80

        self.ATTACK_INVINCIBILITY_TIME_LIMIT = 13
        self.invincibility_timecount = 0
        self.invincibility_timer_active = False
        self.image_showing = True

        self.animation_speed = self.attributes[self.npc]["animation_speed"]
        self.animation_frames_list = self.attributes[self.npc]["animation_frames_list"]
        self.animation_frame = 0
        self.animation_timer = 0


    def update_animation_frame(self):
        self.animation_timer += 1
        if self.animation_timer <= self.animation_speed:
            return
        self.animation_timer = 0
        if self.animation_frame == len(self.animation_frames_list) - 1:
            self.animation_frame = 0
        else:
            self.animation_frame += 1

        self.raw_image = pygame.image.load(f"assets/npc/underworld/{self.npc}/{self.animation_frames_list[self.animation_frame]}.png").convert_alpha()
        self.image = self.raw_image.copy()

    def check_projectile_held_and_create(self):
        if self.attack_type != "ranged":
            return
        if self.holding_projectile:
            return
        self.projectile = Projectile(projectile_group, self)
        self.holding_projectile = True

    def move_projectile_with_player(self):
        if self.attack_type == "ranged":
            self.projectile.update_weapon_position()

    def take_damage(self, weapon):
        weapon_damage = weapon.damage

        if not self.invincibility_timer_active:
            self.play_random_sfx_from_list(self.damage_sfx)
            self.invincibility_timer_active = True
            self.invincibility_timecount = 0
            self.health -= weapon_damage
            self.set_knockback_position(weapon)

        if self.health <= 0:
            self.play_random_sfx_from_list(self.death_sfx)
            if self.attack_type == "ranged":
                self.projectile.kill()
            self.die()

    def set_knockback_position(self, weapon):
        weapon_direction = weapon.player_direction
        weapon_knockback = weapon.knockback
        knockback_effect = max(0, weapon_knockback - self.knockback_resistance)
        if weapon_direction == "left":
            self.knockbackx = self.rect.x - knockback_effect
        elif weapon_direction == "right":
            self.knockbackx = self.rect.x + knockback_effect
        elif weapon_direction == "up":
            self.knockbacky = self.rect.y - knockback_effect
        elif weapon_direction == "down":
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

    def apply_lighting_from_player(self, player_mid_coords):
        self.image = self.raw_image.copy()
        player_gridx = player_mid_coords[0] // settings.UNDERWORLD_TILE_SIZE
        player_gridy = player_mid_coords[1] // settings.UNDERWORLD_TILE_SIZE
        distance = ((self.gridx - player_gridx) ** 2 + (self.gridy - player_gridy) ** 2) ** 0.5
        darkenmax = (255, 255, 255)
        
        #These two statements are to speed up the algorithm
        if distance > 14.7:
            return
        if distance > 8.1:
            self.image.fill(darkenmax, special_flags=pygame.BLEND_RGB_SUB)
        
        DARKNESS_PARAMETER = 0.8 #1 Max
        
        darken1 = (50*DARKNESS_PARAMETER, 60*DARKNESS_PARAMETER, 60*DARKNESS_PARAMETER)
        darken2 = (70*DARKNESS_PARAMETER, 80*DARKNESS_PARAMETER, 80*DARKNESS_PARAMETER) 
        darken3 = (90*DARKNESS_PARAMETER, 100*DARKNESS_PARAMETER, 100*DARKNESS_PARAMETER)
        darken4 = (110*DARKNESS_PARAMETER, 120*DARKNESS_PARAMETER, 120*DARKNESS_PARAMETER)
        darken5 = (130*DARKNESS_PARAMETER, 140*DARKNESS_PARAMETER, 140*DARKNESS_PARAMETER)
        darken6 = (150*DARKNESS_PARAMETER, 160*DARKNESS_PARAMETER, 160*DARKNESS_PARAMETER)
        darken7 = (170*DARKNESS_PARAMETER, 180*DARKNESS_PARAMETER, 180*DARKNESS_PARAMETER)
        darken8 = (190*DARKNESS_PARAMETER, 200*DARKNESS_PARAMETER, 200*DARKNESS_PARAMETER)
        darken9 = (210*DARKNESS_PARAMETER, 220*DARKNESS_PARAMETER, 220*DARKNESS_PARAMETER)
        if distance <= 1:
            self.image.fill(darken1, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 1.41 + 0.05:
            self.image.fill(darken2, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 2.24 + 0.05:
            self.image.fill(darken3, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 3.16 + 0.05:
            self.image.fill(darken4, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 4.12 + 0.05:
            self.image.fill(darken5, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 5.1 + 0.05:
            self.image.fill(darken6, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 6.08 + 0.05:
            self.image.fill(darken7, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 7.07 + 0.05:
            self.image.fill(darken8, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 8.06 + 0.05:
            self.image.fill(darken9, special_flags=pygame.BLEND_RGB_SUB)

    def detect_tile_collisions(self, camera_group, xspeed, yspeed):
        for sprite in camera_group:
            if sprite.type == "tile":
                collide = sprite.rect.colliderect(self.rect)
                if collide:
                    if sprite.tile not in underworld.tiles.WALKABLE:
                        if xspeed > 0:
                            self.rect.right = sprite.rect.left
                        elif xspeed < 0:
                            self.rect.left = sprite.rect.right
                        if yspeed > 0:
                            self.rect.bottom = sprite.rect.top
                        elif yspeed < 0:
                            self.rect.top = sprite.rect.bottom

    def update_grid_locations(self):
        self.gridx = self.rect.x // settings.UNDERWORLD_TILE_SIZE
        self.gridy = self.rect.y // settings.UNDERWORLD_TILE_SIZE
                
    def manage_invincibility_state(self):
        if self.invincibility_timer_active:
            self.invincibility_timecount += 1
            if self.invincibility_timecount >= self.ATTACK_INVINCIBILITY_TIME_LIMIT:
                self.invincibility_timer_active = False
                self.invincibility_timecount = 0

    def play_random_sfx_from_list(self, sfx_list):
        sfx_list = sfx_list
        random_sfx_num = random.randint(0, len(sfx_list) - 1)
        sfx = pygame.mixer.Sound(f"assets/sfx/underworld/{self.npc}/{sfx_list[random_sfx_num]}")
        sfx.play()

    def basic_pathfind(self, player, underworldcamera):
        if self.knockbackx != None or self.knockbacky != None:
            return
        player_rect = player.rect
        player_center_pos = player_rect.center
        distance_from_player = calculate_distance_pythagoras(self.rect.center, player_center_pos)
        #print(f"Distance from player: {distance_from_player} attack range: {self.attack_range}")
        if distance_from_player <= self.attack_range:
            self.attack_sequence(player)
            return
        if distance_from_player < self.aggression_distance:
            if self.rect.x < player_center_pos[0]:
                self.rect.x += self.speed
                self.direction = "right"
                self.detect_tile_collisions(underworldcamera, self.speed, 0)
            elif self.rect.x > player_center_pos[0]:
                self.rect.x -= self.speed
                self.direction = "left"
                self.detect_tile_collisions(underworldcamera, -self.speed, 0)
            if self.rect.y < player_center_pos[1]:
                self.rect.y += self.speed
                self.direction = "down"
                self.detect_tile_collisions(underworldcamera, 0, self.speed)
            elif self.rect.y > player_center_pos[1]:
                self.rect.y -= self.speed
                self.direction = "up"
                self.detect_tile_collisions(underworldcamera, 0, -self.speed)
            self.update_animation_frame()

    def melee_attack(self, player):
        player.take_damage(self)

    def ranged_attack(self, player):
        if self.projectile == None:
            return
        if self.projectile_timer > self.PROJECTILE_THROW_COOLDOWN_TIMER:
            self.projectile_timer = 0
            self.projectile.initialise_throw(player)



    def attack_sequence(self, player):
        if self.attack_type == "melee":
            self.melee_attack(player)
        elif self.attack_type == "ranged":
            self.ranged_attack(player)

        #print("Attack sequence launched: ", self.randomid)

    def custom_update(self, player, camera):
        self.perform_knockback(camera)
        self.basic_pathfind(player, camera)
        
    def increment_projectile_timer(self):
        if self.holding_projectile:
            self.projectile_timer += 1

    def update(self):
        self.increment_projectile_timer()
        self.update_grid_locations()
        self.manage_invincibility_state()
        self.check_projectile_held_and_create()
        self.move_projectile_with_player()
        #print("alive ", self.randomid)
        
        #self.image_flash_refresh()
    
    def drop_coins(self):
        Coin(coin_group, self.rect.centerx, self.rect.centery, self.coins_dropped)

    def die(self):
        self.drop_coins()
        self.kill()
        self.alive = False
        
class Projectile(pygame.sprite.Sprite):
    def __init__(self, pygame_group, npc):
        super().__init__(pygame_group)
        self.parent = npc
        self.type = "projectile"
        self.raw_image = pygame.image.load(f"assets/npc/underworld/projectiles/spear.png").convert_alpha()
        self.image = self.raw_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = -999
        self.rect.y = -999
        self.in_thrown_state = False
        self.honing_coordinates = None
        self.update_weapon_position()
        
        self.MAX_LIFE_TIMER = 40
        self.life_timer = 0

        self.honing_speed = 1/20


    def update_weapon_position(self):
        if self.honing_coordinates == None:
            X_OFFSET_FROM_NPC = 8
            Y_OFFSET_FROM_NPC = -18
            npc_center = self.parent.rect.center
            self.rect.x = npc_center[0] + X_OFFSET_FROM_NPC
            self.rect.y = npc_center[1] + Y_OFFSET_FROM_NPC

    def check_player_collision(self, player):
        if not self.in_thrown_state:
            return
        if self.rect.colliderect(player.rect):
            player.take_damage(self.parent)
            self.kill_custom()

    def initialise_throw(self, player):
        if self.in_thrown_state:
            return
        self.in_thrown_state = True
        self.honing_coordinates = (player.rect.center[0], player.rect.center[1])
        self.abs_x_diff = int(self.honing_speed * abs(self.rect.x - self.honing_coordinates[0]))
        self.abs_y_diff = int(self.honing_speed * abs(self.rect.y - self.honing_coordinates[1]))

    def rotate_spear(self):
        if self.honing_coordinates:
            x1, y1 = self.rect.center
            x2, y2 = self.honing_coordinates
            
            # Calculate the angle in radians
            angle_radians = math.atan2(y2 - y1, x2 - x1)
            
            # Convert to degrees
            angle_degrees = math.degrees(angle_radians) + 90
            
            # Rotate image (negative because Pygame rotates counter-clockwise)
            self.image = pygame.transform.rotate(self.raw_image, -angle_degrees)
            
            # Update rect to center the rotated image
            self.rect = self.image.get_rect(center=(x1, y1))
        

    def perform_throw_honing_movement(self):
        if self.honing_coordinates == None:
            return
        #print(f"{self.parent.randomid} Honing to {self.honing_coordinates}. Xdiff: {self.abs_x_diff}")
        if self.rect.centerx < self.honing_coordinates[0]:
            self.rect.x += self.abs_x_diff
        elif self.rect.centerx > self.honing_coordinates[0]:
            self.rect.x -= self.abs_x_diff
        if self.rect.centery < self.honing_coordinates[1]:
            self.rect.y += self.abs_y_diff
        elif self.rect.centery > self.honing_coordinates[1]:
            self.rect.y -= self.abs_y_diff
        
        self.rotate_spear()
        
        #print(f"Distance: {calculate_distance_pythagoras(self.rect.center, self.honing_coordinates)}")
        if calculate_distance_pythagoras(self.rect.center, self.honing_coordinates) < 14:
            self.kill_custom()
            self.honing_coordinates = None

    def kill_custom(self):
        #Needed to re-initialise spear in parent npc
        self.parent.holding_projectile = False
        self.kill()

    def update_life_timer(self):
        if self.honing_coordinates == None:
            return
        if self.life_timer < self.MAX_LIFE_TIMER:
            self.life_timer += 1
            print(self.life_timer)
            return
        self.kill_custom()

    def update(self):
        self.perform_throw_honing_movement()
        self.update_life_timer()


class Coin(pygame.sprite.Sprite):
    def __init__(self, pygame_group, startx, starty, value):
        super().__init__(pygame_group)
        self.type = "coin"
        self.value = value
        self.ignorecolour = (255, 0, 255)
        self.raw_image = pygame.image.load(f"assets/other/underworld/coin.png").convert_alpha()
        self.image = self.raw_image.copy()

        self.rect = self.image.get_rect()
        self.rect.x = startx
        self.rect.y = starty
    
    def play_random_sfx_from_list(self):
        sfx_list = ["coin.mp3"]
        random_sfx_num = random.randint(0, len(sfx_list) - 1)
        sfx = pygame.mixer.Sound(f"assets/sfx/underworld/coin/{sfx_list[random_sfx_num]}")
        sfx.play()

    def detect_coin_collision(self, player):
        if self.rect.colliderect(player.rect):
            player.coins_collected += self.value
            self.play_random_sfx_from_list()
            self.kill()