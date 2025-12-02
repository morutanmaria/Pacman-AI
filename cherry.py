
import pygame

class Cherry(pygame.sprite.Sprite):
    def __init__(self, x, y, radius=10):
        super().__init__()
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 0, 0), (radius, radius), radius)
        pygame.draw.rect(self.image, (20, 120, 20), (radius-2, 0, 4, 6))
        self.rect = self.image.get_rect(center=(x, y))
