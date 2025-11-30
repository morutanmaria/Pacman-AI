import pygame
from settings import PINK
import math

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
        self.direction = (1, 0)
        self.mouth_angle = 30
        

    def update(self, keys_pressed, walls):
        dx = dy = 0
    
        if keys_pressed[pygame.K_LEFT]:
            dx = -self.speed
            self.direction = (-1, 0)
        if keys_pressed[pygame.K_RIGHT]:
            dx = self.speed
            self.direction = (1, 0)
        if keys_pressed[pygame.K_UP]:
            dy = -self.speed
            self.direction = (0, -1)
        if keys_pressed[pygame.K_DOWN]:
            dy = self.speed
            self.direction = (0, 1)

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
        self.redraw()

    def redraw(self):
        self.image.fill((0, 0, 0, 0))

        center = (self.radius, self.radius)
        r = self.radius
        mouth_angle = math.radians(self.mouth_angle)

        dx, dy = self.direction
        angle = math.atan2(-dy, dx)

        start_angle = angle + mouth_angle
        end_angle = angle - mouth_angle
        pygame.draw.circle(self.image, PINK, center, r)

        cut_length = r * 2.2
        p1 = center
        p2 = (
            center[0] + cut_length * math.cos(start_angle),
            center[1] - cut_length * math.sin(start_angle)
        )
        p3 = (
            center[0] + cut_length * math.cos(end_angle),
            center[1] - cut_length * math.sin(end_angle)
        )

        pygame.draw.polygon(self.image, (0, 0, 0, 0), [p1, p2, p3])

        eye_positions = {
        (1, 0):  (10, 10),
        (-1, 0): (20, 10),
        (0, -1): (6, 16),
        (0, 1):  (24, 14)
        }

        eye_radius = 30 // 6
        pupil_radius = 30 // 12
        eye_x, eye_y = eye_positions.get(self.direction, (10, 10))

        pygame.draw.circle(self.image, (255, 255, 255), (eye_x, eye_y), eye_radius)
        pygame.draw.circle(self.image, (0, 0, 0), (eye_x, eye_y), pupil_radius)
