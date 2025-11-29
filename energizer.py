import pygame
from settings import WHITE, TILE_SIZE

class Energizer(pygame.sprite.Sprite):
    def __init__(self, x, y, radius = 12):
        super().__init__()
        self.image = pygame.Surface((radius*2, radius*2))
        pygame.draw.circle(self.image, WHITE, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))