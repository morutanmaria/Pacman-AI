import pygame
import random
from collections import deque
from settings import TILE_SIZE
from settings import BLUE_BUHUHU
import heapq

class Ghost(pygame.sprite.Sprite):
    def __init__(self, x, y, maze, color):
        super().__init__()
        
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        self.original_color = color
        self.color = color
        T = TILE_SIZE

        self.start_x = x
        self.start_y = y

        body_rect = pygame.Rect(0, T // 4, T, T * 3 // 4)
        pygame.draw.rect(self.image, self.color, body_rect, border_radius = T // 4)
        pygame.draw.circle(self.image, self.color, (T // 2, T // 2), T // 2)

        # eye_radius = T // 6
        # pupil_radius = T // 12
        # pygame.draw.circle(self.image, (255, 255, 255), (T // 3, T // 3), eye_radius)
        # pygame.draw.circle(self.image, (0, 0, 0), (T // 3, T // 3), pupil_radius)

        # pygame.draw.circle(self.image, (255, 255, 255), (T * 2 // 3, T // 3), eye_radius)
        # pygame.draw.circle(self.image, (0, 0, 0), (T * 2 // 3, T // 3), pupil_radius)
        self.rect = self.image.get_rect(topleft=(x, y))

        self.maze = maze  
        self.frightened = False
        self.speed = 2
        self.direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        self.walls_group = None

    def update_eyes(self):
        T = TILE_SIZE
        dx, dy = self.direction
        
        offset = T // 8
        ox = dx * offset
        oy = dy * offset

        self.image.fill((0, 0, 0, 0))

        body_rect = pygame.Rect(0, T // 4, T, T * 3 // 4)
        pygame.draw.rect(self.image, self.color, body_rect, border_radius=T // 4)
        pygame.draw.circle(self.image, self.color, (T // 2, T // 2), T // 2)

        pygame.draw.circle(self.image, (255,255,255), (T//3, T//3), T//6)
        pygame.draw.circle(self.image, (255,255,255), (2*T//3, T//3), T//6)

        pygame.draw.circle(self.image, (0,0,0), (T//3 + ox, T//3 + oy), T//12)
        pygame.draw.circle(self.image, (0,0,0), (2*T//3 + ox, T//3 + oy), T//12)


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
        if hasattr(self, "mode") and self.mode == "frightened":
            mode = "frightened"
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
            elif mode == "frightened":
                self.speed = 1
                self.frightened = True
                self.random_ai()
                if pygame.time.get_ticks() - self.frightened_timer_start > self.frightened_duration:
                    self.speed = 2
                    self.frightened = False
                    self.mode = None
                    self.color = self.original_color

        old_x, old_y = self.rect.x, self.rect.y
        if len(self.direction) == 2:
            dx, dy = self.direction
        else:
            dx, dy = (0, 0)

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
        self.update_eyes()


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

    def set_frightened_mode(self):
        if not self.frightened:
            self.mode = "frightened"
            self.frightened = True
            self.frightened_timer_start = pygame.time.get_ticks() 
            self.frightened_duration = 8000
            currentx , currenty = self.direction
            self.direction = (-currentx, -currenty)
        self.frightened_timer_start = pygame.time.get_ticks()
        self.frightened_duration = 8000
        self.color = BLUE_BUHUHU
    
    def reset_position(self):
        self.rect.topleft = (self.start_x, self.start_y)

    def dfs_full_path(self, start, goal):
        stack = [start]
        visited = {start: None}

        while stack:
            current = stack.pop()
            if current == goal:
                break

            cx, cy = current
            #ordinea vecinilor influenteaza dfs
            neighbors = [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]

            for nx, ny in neighbors:
                if (0<=nx<len(self.maze[0]) and
                        0<=ny<len(self.maze) and
                        self.maze[ny][nx] != 1 and
                        (nx, ny) not in visited):
                    visited[(nx, ny)] = current
                    stack.append((nx, ny))

        #dacă nu gaseste drumul
        if goal not in visited:
            return []

        #construire path complet
        path = []
        cur = goal
        while cur != start:
            path.append(cur)
            cur = visited[cur]
        path.reverse()
        return path

    def bfs_full_path(self, start, goal):
        from collections import deque
        queue = deque([start])
        visited = {start: None}

        while queue:
            current = queue.popleft()
            if current == goal:
                break

            cx, cy = current
            for nx, ny in [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]:
                if (0<=nx<len(self.maze[0]) and 0<=ny<len(self.maze)):
                    if self.maze[ny][nx] != 1 and (nx, ny) not in visited:
                        visited[(nx, ny)] = current
                        queue.append((nx, ny))

        if goal not in visited:
            return []

        #construire path complet
        path = []
        cur = goal
        while cur != start:
            path.append(cur)
            cur = visited[cur]
        path.reverse()
        return path

    def astar_full_path(self, start, goal):
        import heapq
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
            for nx, ny in [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]:
                if (0<=nx<len(self.maze[0]) and
                        0<=ny<len(self.maze) and
                        self.maze[ny][nx] != 1):

                    tg = g_score[current]+1
                    if (nx, ny) not in g_score or tg < g_score[(nx, ny)]:
                        came_from[(nx, ny)] = current
                        g_score[(nx, ny)] = tg
                        f_score[(nx, ny)] = tg + self.hmd((nx, ny), goal)

                        if (nx, ny) not in open_set:
                            count += 1
                            heapq.heappush(open_heap, (f_score[(nx, ny)], count, (nx, ny)))
                            open_set.add((nx, ny))

        if goal not in came_from:
            return []

        #construire path complet
        path = []
        cur = goal
        while cur != start:
            path.append(cur)
            cur = came_from[cur]
        path.reverse()
        return path
