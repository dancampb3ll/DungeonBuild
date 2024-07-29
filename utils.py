import pygame

floating_text_group = pygame.sprite.Group()

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