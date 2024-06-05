import pygame
import random
import math
import settings
import underworld

def calculate_distance_pythagoras(point1: tuple, point2: tuple):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

class Npc(pygame.sprite.Sprite):
    def __init__(self, pygame_group, gridx, gridy, npctype):
        super().__init__(pygame_group)
        self.type = "npc"
        self.npc = npctype
        self.health = 5
        self.ignorecolour = (255, 0, 255)
        self.raw_image = pygame.image.load(f"assets/npc/underworld/{self.npc}.png").convert_alpha()
        self.image = self.raw_image.copy()

        self.rect = self.image.get_rect()
        self.gridx = gridx
        self.gridy = gridy
        self.rect.x = self.gridx * settings.UNDERWORLD_TILE_SIZE
        self.rect.y = self.gridy * settings.UNDERWORLD_TILE_SIZE
        
        
        self.attributes = {
            "slime": {
                "damage_sfx": ["take_damage1.mp3"],
                "death_sfx": ["death1.mp3"],
                "aggression_distance": 280,
                "knockback_resistance_min": 4,
                "knockback_resistance_max": 8,
                "speed_min" : 100,
                "speed_max" : 100
            }
        }
        self.aggression_distance = self.attributes[self.npc]["aggression_distance"]
        self.damage_sfx = self.attributes[self.npc]["damage_sfx"]
        self.death_sfx = self.attributes[self.npc]["death_sfx"]
        self.knockback_resistance_min = self.attributes[self.npc]["knockback_resistance_min"]
        self.knockback_resistance_max = self.attributes[self.npc]["knockback_resistance_max"]
        self.knockback_resistance = random.randint(self.knockback_resistance_min, self.knockback_resistance_max)
        self.speed_min = self.attributes[self.npc]["speed_min"]
        self.speed_max = self.attributes[self.npc]["speed_max"]
        self.speed = random.randint(self.speed_min, self.speed_max) / 100

        self.knockbackx = None
        self.knockbacky = None

        self.ATTACK_INVINCIBILITY_TIME_LIMIT = 13
        self.invincibility_timecount = 0
        self.invincibility_timer_active = False
        self.image_showing = True

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

    def perform_knockback(self):
        if self.knockbackx == None and self.knockbacky == None:
            return
        knockback_speed = settings.KNOCKBACK_SPEED

        if self.knockbackx != None:
            if self.knockbackx > self.rect.x:
                self.rect.x = min(self.knockbackx, self.rect.x + knockback_speed)
            elif self.knockbackx < self.rect.x:
                self.rect.x = max(self.knockbackx, self.rect.x - knockback_speed)
            else:
                self.knockbackx = None

        if self.knockbacky != None:
            if self.knockbacky > self.rect.y:
                self.rect.y = min(self.knockbacky, self.rect.y + knockback_speed)
            elif self.knockbacky < self.rect.y:
                self.rect.y = max(self.knockbacky, self.rect.y - knockback_speed)
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

    def die(self):
        self.kill()

    """
        def image_flash_refresh(self):
            FLASH_MODULUS = 6
            if self.invincibility_timer_active == False:
                self.image_showing = True
                self.image = self.image_visible
                return
            if self.invincibility_timecount % FLASH_MODULUS == 0:
                self.image_showing = not self.image_showing
                if self.image_showing == True:
                    self.image = self.image_visible
                else:
                    self.image = self.image_invisible
    """
                
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
        if self.rect.collidepoint(player_rect.center):
            self.attack_sequence(player)
            return
        if distance_from_player < self.aggression_distance:
            if self.rect.x < player_center_pos[0]:
                self.rect.x += self.speed
                self.detect_tile_collisions(underworldcamera, self.speed, 0)
            elif self.rect.x > player_center_pos[0]:
                self.rect.x -= self.speed
                self.detect_tile_collisions(underworldcamera, -self.speed, 0)
            if self.rect.y < player_center_pos[1]:
                self.rect.y += self.speed
                self.detect_tile_collisions(underworldcamera, 0, self.speed)
            elif self.rect.y > player_center_pos[1]:
                self.rect.y -= self.speed
                self.detect_tile_collisions(underworldcamera, 0, -self.speed)

    def attack_sequence(self, player):
        None

    def update(self):
        self.update_grid_locations()
        self.manage_invincibility_state()
        self.perform_knockback()
        #self.image_flash_refresh()
        
        