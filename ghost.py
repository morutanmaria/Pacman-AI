import pygame
import random
from collections import deque
from settings import TILE_SIZE, BLUE

class Ghost(pygame.sprite.Sprite):
    def __init__(self, x, y, maze, color=(255, 0, 0)):
        super().__init__()
        
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

        self.maze = maze  

        self.speed = 2
        self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

    def get_tile(self):
        """Return current tile in the maze grid."""
        return (self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE)

    def set_direction(self, direction):
        self.direction = direction

    def valid_moves(self, tile):
        """Return all open neighbors from a tile (x,y)."""
        x, y = tile
        neighbors = []

        options = {
            (1,0):  (x+1, y),
            (-1,0): (x-1, y),
            (0,1):  (x, y+1),
            (0,-1): (x, y-1),
        }

        for dir, (nx, ny) in options.items():
            if 0 <= nx < len(self.maze[0]) and 0 <= ny < len(self.maze):
                if self.maze[ny][nx] == 0:  
                    neighbors.append((dir, (nx, ny)))

        return neighbors

    def random_ai(self):
        tile = self.get_tile()
        moves = self.valid_moves(tile)
        
        if not moves:
            return  

        if random.random() < 0.1:
            dir, tile = random.choice(moves)
            self.direction = dir

    def chase_ai(self, player):
        px, py = player.rect.centerx, player.rect.centery
        gx, gy = self.rect.centerx, self.rect.centery

        tile = self.get_tile()
        moves = self.valid_moves(tile)

        if not moves:
            return

        best_move = None
        best_dist = 999999

        for dir, (tx, ty) in moves:
            cx = tx * TILE_SIZE + TILE_SIZE // 2
            cy = ty * TILE_SIZE + TILE_SIZE // 2

            dist = (cx - px)**2 + (cy - py)**2
            if dist < best_dist:
                best_dist = dist
                best_move = dir

        if best_move:
            self.direction = best_move

    def bfs(self, start, goal):
        """Return next step using BFS from start tile to goal tile."""
        
        queue = deque([start])
        visited = {start: None}

        while queue:
            current = queue.popleft()
            if current == goal:
                break

            cx, cy = current
            options = [(cx+1,cy), (cx-1,cy), (cx,cy+1), (cx,cy-1)]

            for nx, ny in options:
                if (0 <= ny < len(self.maze)
                    and 0 <= nx < len(self.maze[0])
                    and self.maze[ny][nx] == 0
                    and (nx,ny) not in visited):

                    visited[(nx,ny)] = current
                    queue.append((nx,ny))

        if goal not in visited:
            return None

        step = goal
        while visited[step] != start:
            step = visited[step]
        return step  

    def smart_ai(self, player):
        start = self.get_tile()
        px = player.rect.centerx // TILE_SIZE
        py = player.rect.centery // TILE_SIZE
        goal = (px, py)

        next_tile = self.bfs(start, goal)
        if not next_tile:
            return  

        sx, sy = start
        nx, ny = next_tile

        if nx > sx: self.direction = (1,0)
        if nx < sx: self.direction = (-1,0)
        if ny > sy: self.direction = (0,1)
        if ny < sy: self.direction = (0,-1)

    def update(self, player, mode="random"):
        if mode == "random":
            self.random_ai()
        elif mode == "chase":
            self.chase_ai(player)
        elif mode == "smart":
            self.smart_ai(player)

        dx, dy = self.direction
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
