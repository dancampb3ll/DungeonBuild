from main import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pygame_group):
        super().__init__(pygame_group)
        self.type = "player"
        self.image = pygame.image.load("assets/player.png").convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT // 2
        self.speed = PLAYERSPEED
        self.debug = ""
        
        self.buildmode = False
        self.B_key_down = False
        self.top_left_highlighted_sprite = None

    def detect_tile_collisions(self, camera_group, xspeed, yspeed):
        collide_count = 0
        for sprite in camera_group:
            if sprite.type == "tile":
                collide = sprite.rect.colliderect(self.rect)
                if collide:
                    collide_count += 0
                    if sprite.tile not in WALKABLE_TILES:
                        if xspeed > 0:
                            self.rect.right = sprite.rect.left
                        elif xspeed < 0:
                            self.rect.left = sprite.rect.right
                        if yspeed > 0:
                            self.rect.bottom = sprite.rect.top
                        elif yspeed < 0:
                            self.rect.top = sprite.rect.bottom

    def move_player(self, camera_group):
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
            self.rect.x -= self.speed
            self.detect_tile_collisions(camera_group, -self.speed, 0)
        #right
        elif key[pygame.K_d]:
            self.rect.x += self.speed
            self.detect_tile_collisions(camera_group, self.speed, 0)
        #down
        if key[pygame.K_s]:
            self.rect.y += self.speed
            self.detect_tile_collisions(camera_group, 0, self.speed)
        #up
        elif key[pygame.K_w]:
            self.rect.y -= self.speed
            self.detect_tile_collisions(camera_group, 0, -self.speed)

    def check_build_mode(self, input_events, buildhud, camera_group):
        for event in input_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b and not self.B_key_down:
                    self.toggle_build_mode(buildhud, camera_group)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_b:
                    self.B_key_down = False

    def toggle_build_mode(self, buildhud, camera_group):
        if self.buildmode == False:
            self.buildmode = True
            buildhud.show()
        else:
            self.buildmode = False
            buildhud.hide()
            self.reset_tile_highlights(camera_group)

    
    def reset_tile_highlights(self, camera_group):
        for sprite in camera_group.sprites():
            if sprite.type == "tile":
                sprite.image = sprite.original_image.copy()

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
                        sprite.image = sprite.original_image.copy()

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
                raw_mouse_pos = event.pos
                offset_adjusted_mouse_pos = (raw_mouse_pos[0] + camera_group.offset.x, raw_mouse_pos[1] + camera_group.offset.y)
                placement_coords = (offset_adjusted_mouse_pos[0] // TILE_SIZE, offset_adjusted_mouse_pos[1] // TILE_SIZE)
        
        if placement_coords is None:
            return None

        print(placement_coords)
        return placement_coords
        #Will work by checking if tile is made of border. If yes, replace with grass.
        #Will need to add function in gameloop which checks world and applies border to adjacent cells

    def update(self):
        None
        #print((self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE))
        #debug = f"self.rect.center {self.rect.center} | self.rect.bottomleft {self.rect.bottomleft} | self.rect.topright {self.rect.topright} | self.rect.center tile {self.rect.center[0] // (TILE_SIZE)} | self.rect.bottomleft tile {self.rect.bottomleft[0] // TILE_SIZE} | self.rect.topright tile {self.rect.topright[0] // TILE_SIZE}"
        #if debug != self.debug:
        #    self.debug = debug
        #    print(self.debug)