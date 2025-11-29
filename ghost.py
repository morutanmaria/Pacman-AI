import pygame
import random
from collections import deque
from settings import TILE_SIZE, BLUE
import heapq

class Ghost(pygame.sprite.Sprite):
    def __init__(self, x, y, maze, color=(255, 0, 0)):
        super().__init__()
        
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

        self.maze = maze  

        self.speed = 2
        self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        self.walls_group = None

    def set_walls(self, walls_group):
        self.walls_group = walls_group

    def get_tile(self):
        """Return current tile in the maze grid."""
        return (self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE)

    def at_tile_center(self):
        return (self.rect.centerx % TILE_SIZE == TILE_SIZE // 2 and
            self.rect.centery % TILE_SIZE == TILE_SIZE // 2)

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
                if self.maze[ny][nx] != 1:
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
                    and self.maze[ny][nx] != 1
                    and (nx,ny) not in visited):

                    visited[(nx,ny)] = current
                    queue.append((nx,ny))

        if goal not in visited:
            return None
        
        if goal == start:
            return None

        step = goal
        while visited[step] != start:
            step = visited[step]
        return step  

    #nu cred ca mai avem nevoie de smart_ai, poate fi sters, este functia move_to_tile si pentru dfs si astar
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

    def hmd(self, p1: tuple[int, int], p2: tuple[int, int]) -> float:
        x1, y1 = p1
        x2, y2 = p2
        return abs(x1 - x2) + abs(y1 - y2)

    def dfs(self, start, goal):
        """Return next step using DFS from start tile to goal tile."""
        stack = [start]
        visited = {start: None} 

        while stack:
            current = stack.pop()
            if current == goal:
                break

            cx, cy = current
            options = [(cx+1,cy), (cx-1,cy), (cx,cy+1), (cx,cy-1)]
            
            random.shuffle(options)

            for nx, ny in options:
                if (0 <= ny < len(self.maze)
                    and 0 <= nx < len(self.maze[0])
                    and self.maze[ny][nx] != 1
                    and (nx,ny) not in visited):

                    visited[(nx,ny)] = current
                    stack.append((nx,ny))

        if goal not in visited:
            return None
        
        if goal == start:
            return None

        step = goal
        while visited[step] != start:
            step = visited[step]
        return step

    def astar(self, start, goal):
        """Return next step using A* from start tile to goal tile."""
        count = 0
        open_heap = []
        heapq.heappush(open_heap, (0, count, start))

        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.hmd(start, goal)}
        
        open_set = {start}

        while open_heap:
            current = heapq.heappop(open_heap)[2]
            open_set.remove(current)

            if current == goal:
                break
                
            cx, cy = current
            options = [(cx+1,cy), (cx-1,cy), (cx,cy+1), (cx,cy-1)]

            for nx, ny in options:
                if not (0 <= ny < len(self.maze) and 0 <= nx < len(self.maze[0])):
                    continue
                if self.maze[ny][nx] == 1:
                    continue
                
                tentative_g = g_score[current] + 1
                
                if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                    came_from[(nx, ny)] = current 
                    g_score[(nx, ny)] = tentative_g
                    f_score[(nx, ny)] = tentative_g + self.hmd((nx, ny), goal)
                    
                    if (nx, ny) not in open_set:
                        count += 1
                        heapq.heappush(open_heap, (f_score[(nx, ny)], count, (nx, ny)))
                        open_set.add((nx, ny))

        if goal not in came_from:
            return None

        step = goal
        while came_from[step] != start:
            step = came_from[step]
        return step

    def update(self, player, mode="random"):
        if self.at_tile_center():
            start = self.get_tile()
            px = player.rect.centerx // TILE_SIZE
            py = player.rect.centery // TILE_SIZE
            goal = (px, py)
            
            if mode == "random":
                self.random_ai()
            elif mode == "chase":
                self.chase_ai(player)
            elif mode == "bfs":
                next_tile = self.bfs(start, goal)
                if next_tile:
                    self.move_to_tile(next_tile)
            elif mode == "dfs":
                next_tile = self.dfs(start, goal)
                if next_tile:
                    self.move_to_tile(next_tile)
            elif mode == "astar":
                next_tile = self.astar(start, goal)
                if next_tile:
                    self.move_to_tile(next_tile)
        
        old_x, old_y = self.rect.x, self.rect.y
        
        dx, dy = self.direction
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        
        if self.walls_group and pygame.sprite.spritecollide(self, self.walls_group, False):
            self.rect.x, self.rect.y = old_x, old_y
            self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        
        maze_width = len(self.maze[0]) * TILE_SIZE
        maze_height = len(self.maze) * TILE_SIZE
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > maze_width:
            self.rect.right = maze_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > maze_height:
            self.rect.bottom = maze_height

    def move_to_tile(self, next_tile):
        """Set direction towards next tile"""
        if not next_tile:
            return
            
        sx, sy = self.get_tile()
        nx, ny = next_tile
        
        if abs(nx - sx) + abs(ny - sy) != 1:
            return
        
        if nx > sx: 
            self.direction = (1, 0)
        elif nx < sx: 
            self.direction = (-1, 0)
        elif ny > sy: 
            self.direction = (0, 1)
        elif ny < sy: 
            self.direction = (0, -1)