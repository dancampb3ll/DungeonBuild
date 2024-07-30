import pygame
import settings

DARKNESS_PARAMETER = 0.7 #1 is Max darkness, 0.7 recommended

def apply_lighting_from_player(raw_image, self_mid_coords, player_mid_coords):
        image = raw_image.copy()
        player_gridx = player_mid_coords[0] // settings.UNDERWORLD_TILE_SIZE
        player_gridy = player_mid_coords[1] // settings.UNDERWORLD_TILE_SIZE
        self_gridx = self_mid_coords[0] // settings.UNDERWORLD_TILE_SIZE
        self_gridy = self_mid_coords[1] // settings.UNDERWORLD_TILE_SIZE
        distance = ((self_gridx - player_gridx) ** 2 + (self_gridy - player_gridy) ** 2) ** 0.5
        darkenmax = (255, 255, 255)
        
        #These two statements are to speed up the algorithm by instantly setting a value for far away objects
        if distance > 8.1:
            image.fill(darkenmax, special_flags=pygame.BLEND_RGB_SUB)
            return image
        if distance > 14.7:
            image.fill(darkenmax, special_flags=pygame.BLEND_RGB_SUB)
            return image
        
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
            image.fill(darken1, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 1.41 + 0.05:
            image.fill(darken2, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 2.24 + 0.05:
            image.fill(darken3, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 3.16 + 0.05:
            image.fill(darken4, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 4.12 + 0.05:
            image.fill(darken5, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 5.1 + 0.05:
            image.fill(darken6, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 6.08 + 0.05:
            image.fill(darken7, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 7.07 + 0.05:
            image.fill(darken8, special_flags=pygame.BLEND_RGB_SUB)
        elif distance <= 8.06 + 0.05:
            image.fill(darken9, special_flags=pygame.BLEND_RGB_SUB)
        
        return image