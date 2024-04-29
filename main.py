import pygame

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
TILE_SIZE = 16
TILE_COUNT = SCREEN_HEIGHT / TILE_SIZE
PLAYERSPEED = 1
CAMERASPEED = PLAYERSPEED


#A tile is initialised with a gridx and gridy location. The true x and true y are then multiples of these by the tile size.
class OutdoorTile(pygame.sprite.Sprite):
    def __init__(self, gridx, gridy, tile, pygame_group):
        super().__init__(pygame_group)
        self.image = pygame.image.load(f"assets/{tile}.png").convert()
        self.rect = self.image.get_rect()
        self.gridx = gridx
        self.gridy = gridy
        self.rect.x = gridx * TILE_SIZE
        self.rect.y = gridy * TILE_SIZE
    
    def update(self):
        None
    

class Player(pygame.sprite.Sprite):
    def __init__(self, gridx, gridy, pygame_group):
        super().__init__(pygame_group)
        self.image = pygame.image.load("assets/player.png").convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.gridx = gridx
        self.gridy = gridy
        self.rect.x = gridx * TILE_SIZE
        self.rect.y = gridy * TILE_SIZE

    def move_player(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            self.rect.x -= PLAYERSPEED
        elif key[pygame.K_d]:
            self.rect.x += PLAYERSPEED
        if key[pygame.K_s]:
            self.rect.y += PLAYERSPEED
        elif key[pygame.K_w]:
            self.rect.y -= PLAYERSPEED

    def update(self):
        self.move_player()

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
        self.offset = pygame.math.Vector2(-target.rect.x, -target.rect.y)
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft + self.offset
            self.display_surface.blit(sprite.image, offset_pos)

pygame.init()
 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

pygame.display.set_caption('DungeonBuild')


#Camera must be defined first
cameragroup = CameraGroup()

#Drawing tiles
for i in range(15, 30):
    for j in range(15, 30):
        OutdoorTile(i, j, "overgroundGrass", cameragroup)
for i in range(27, 29):
    for j in range(27, 29):
        OutdoorTile(i, j, "overgroundWater", cameragroup)


player = Player(22, 22, cameragroup)



running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((10, 10, 18))


    cameragroup.custom_draw(player)
    cameragroup.update()
    
    

    pygame.display.update()
    clock.tick(60)
    