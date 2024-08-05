import pygame
import math

floating_text_group = pygame.sprite.Group()

def find_point_on_diagonal_line_between_two_points(x1, y1, x2, y2, xdistance=20000):
    """
    Gets a point at a diagonal line between 2 points, where an x distance is given away from the original x point.
    """
    
    #Prevents errors with both points being the same
    if x2 == x1:
        x2 += 1
    if y2 == y1:
        y2 += 1
    
    m = (y2 - y1) / (x2 - x1)

    if x2 < x1:
        xdistance *= -1

    x3 = x1 + xdistance
    y3 = y1 + xdistance * m

    return (x3, y3)

def calculate_distance_pythagoras(point1: tuple, point2: tuple):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

class FloatingText(pygame.sprite.Sprite):
        def __init__(self, pygame_group, startx, starty, value, time_limit=80, bold_choice=True, font_size=14, colour=(255,255,255)):
            super().__init__(pygame_group)
            self.type = "floatingText"
            self.value = value
            self.text = str(self.value)
            self.FONT_SIZE = font_size
            self.FONT_COLOUR = colour
            self.font = pygame.font.SysFont("Courier New", self.FONT_SIZE, bold=bold_choice)
            self.image = self.font.render(self.text, True, self.FONT_COLOUR)
            self.rect = self.image.get_rect()
            self.rect.x = startx
            self.rect.y = starty

            self.time_limit = time_limit
            self.alive_timer = 0

        def move_position_upwards(self):
            self.rect.y -= 1

        def maintain_life(self):
            self.alive_timer += 1
            if self.alive_timer >= self.time_limit:
                self.kill()

        def update(self):
            self.move_position_upwards()
            self.maintain_life()