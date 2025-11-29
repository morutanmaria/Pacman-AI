import pygame
from settings import PINK

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(PINK)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 5
        

    def update(self, keys_pressed, walls):
        dx = dy = 0
    
        if keys_pressed[pygame.K_LEFT]:
            dx = -self.speed
        if keys_pressed[pygame.K_RIGHT]:
            dx = self.speed
        if keys_pressed[pygame.K_UP]:
            dy = -self.speed
        if keys_pressed[pygame.K_DOWN]:
            dy = self.speed

        self.rect.x += dx
        if pygame.sprite.spritecollide(self, walls, False):
            self.rect.x -= dx

        self.rect.y += dy
        if pygame.sprite.spritecollide(self, walls, False):
            self.rect.y -= dy
