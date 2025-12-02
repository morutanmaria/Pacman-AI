import pygame
from settings import PINK
import math
from settings import TILE_SIZE


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

    def reflex_update(self, walls_group, ghosts_group, pellets_group, energizers_group):
        possible_actions = {
            "UP": (0, -1),
            "DOWN": (0, 1),
            "LEFT": (-1, 0),
            "RIGHT": (1, 0)
        }

        best_score = -99999
        best_action = None

        for action, (dx, dy) in possible_actions.items():
            #simulam mutarea
            new_rect = self.rect.move(dx * TILE_SIZE, dy * TILE_SIZE)

            # verificam pereti
            collision = False
            for wall in walls_group:
                if new_rect.colliderect(wall.rect):
                    collision = True
                    break
            if collision:
                continue

            # calc coord tile
            new_tile_x = new_rect.centerx // TILE_SIZE
            new_tile_y = new_rect.centery // TILE_SIZE

            score = 0

            #ne apropiem de un pellet => scor pozitiv
            for pellet in pellets_group:
                px = pellet.rect.centerx // TILE_SIZE
                py = pellet.rect.centery // TILE_SIZE
                dist = abs(px - new_tile_x) + abs(py - new_tile_y)
                score += 10 / (dist + 1)

            #ne apropiem de un energizer => scor mai mare
            for energizer in energizers_group:
                ex = energizer.rect.centerx // TILE_SIZE
                ey = energizer.rect.centery // TILE_SIZE
                dist = abs(ex - new_tile_x) + abs(ey - new_tile_y)
                score += 20 / (dist + 1)

            #dist de fantome => trebuie sa le evitam
            for ghost in ghosts_group:
                gx, gy = ghost.get_tile()
                dist = abs(gx - new_tile_x) + abs(gy - new_tile_y)

                if ghost.frightened:
                    #cand fantoma e speriata => o mancam
                    score += 40 / (dist + 1)
                else:
                    #normal => fugi
                    score -= 100 / (dist + 1)

            if score > best_score:
                best_score = score
                best_action = (dx, dy)

        if best_action:
            self.direction = best_action

        #facem update-ul normal al miscarii
        self.rect.x +=self.direction[0]*self.speed
        self.rect.y +=self.direction[1]*self.speed
