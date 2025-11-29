import pygame
from settings import PINK

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        self.radius = 15
        pygame.draw.circle(self.image, PINK, (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.image, PINK, (30 // 2, 30 // 2), 30 // 2)

        eye_radius = 30 // 6
        pupil_radius = 30 // 12
        pygame.draw.circle(self.image, (255, 255, 255), (30 // 3, 30 // 3), eye_radius)
        pygame.draw.circle(self.image, (0, 0, 0), (30 // 3, 30 // 3), pupil_radius)
        self.rect= self.image.get_rect(topleft=(x, y))
        self.speed = 4
        

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
        collided_walls = pygame.sprite.spritecollide(self, walls, False)
        if collided_walls:
            for wall in collided_walls:
                if dx > 0:
                    self.rect.right = wall.rect.left
                elif dx < 0:
                    self.rect.left = wall.rect.right


        self.rect.y += dy
        collided_walls = pygame.sprite.spritecollide(self, walls, False)
        if collided_walls:
            for wall in collided_walls:
                if dy > 0:
                    self.rect.bottom = wall.rect.top
                elif dy < 0:
                    self.rect.top = wall.rect.bottom
