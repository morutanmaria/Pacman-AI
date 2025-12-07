import pygame
from settings import PINK
import math
import random 
import heapq
from collections import deque
from game_state import SimulatedState
from settings import TILE_SIZE

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, maze):
        super().__init__()
        self.image = pygame.Surface((30, 30)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        self.radius = 15
        self.current_mode = "manual"
        self.maze = maze
        self.invincible = False
        self.invincible_timer = 0 
        self.invincible_duration = 2000
        self.visible = True
        self.blink_timer = 0
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
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 2000
        self.visible = True
        self.blink_timer = 0

        self.mouth_angle = 30
        self.mouth_opening = False 
        self.mouth_speed = 4 

        

    def _is_food_tile(self, tile, pellets_group, energizers_group):
        tile_center_x = tile[0] * TILE_SIZE + TILE_SIZE // 2
        tile_center_y = tile[1] * TILE_SIZE + TILE_SIZE // 2
        
        tile_rect = pygame.Rect(tile_center_x - 1, tile_center_y - 1, 2, 2)

        if pygame.sprite.spritecollide(tile_rect, pellets_group, False):
            return True

        if pygame.sprite.spritecollide(tile_rect, energizers_group, False):
            return True
            
        return False

    def _is_ghost_nearby(self, tile, ghosts_group, player_mode):
        target_center_x = tile[0] * TILE_SIZE + TILE_SIZE // 2
        target_center_y = tile[1] * TILE_SIZE + TILE_SIZE // 2
        
        for ghost in ghosts_group:
            if hasattr(ghost, 'mode') and ghost.mode == "frightened":
                continue 

            dist_x = abs(target_center_x - ghost.rect.centerx)
            dist_y = abs(target_center_y - ghost.rect.centery)

            if dist_x < TILE_SIZE * 1.5 and dist_y < TILE_SIZE * 1.5:
                return True
                
        return False

    def set_direction(self, direction):
        self.direction = direction

    def update(self, keys_pressed, walls):
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.invincible_timer > self.invincible_duration:
                self.invincible = False
                self.visible = True
            else:
                if current_time - self.blink_timer > 100:
                    self.visible = not self.visible
                    self.blink_timer = current_time
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
            self.direction = (0, 0)
            return
        
        self.rect.y += dy
        collided_walls = pygame.sprite.spritecollide(self, walls, False)
        if collided_walls:
            for wall in collided_walls:
                if dy > 0:
                    self.rect.bottom = wall.rect.top
                elif dy < 0:
                    self.rect.top = wall.rect.bottom
            self.direction = (0, 0)
            return
            
        if not self.invincible or self.visible:
            self.redraw()
        else:
            self.image.fill((0, 0, 0, 0))
        
        if dx != 0 or dy != 0:
            if self.mouth_opening:
                self.mouth_angle += self.mouth_speed
                if self.mouth_angle >= 30:
                    self.mouth_angle = 30
                    self.mouth_opening = False
            else:
                self.mouth_angle -= self.mouth_speed
                if self.mouth_angle <= 0:
                    self.mouth_angle = 0
                    self.mouth_opening = True
        else:
            self.mouth_angle = 0


    def redraw(self):
        self.image.fill((0, 0, 0, 0))

        if self.invincible and not self.visible:
            return
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

    def get_tile(self):
        """Return current tile in the maze grid."""
        return (self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE)

    def at_tile_center(self):
        return (self.rect.centerx % TILE_SIZE == TILE_SIZE // 2 and
            self.rect.centery % TILE_SIZE == TILE_SIZE // 2)

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

    def hmd(self, p1: tuple[int, int], p2: tuple[int, int]) -> float:
        x1, y1 = p1
        x2, y2 = p2
        return abs(x1 - x2) + abs(y1 - y2)

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

    def minimax(self, state: SimulatedState, depth, ghost_index):
        if state.is_terminal() or depth == 0:
            return self.evaluate_state(state)

        if ghost_index == 0:
            if depth == 1:
                return self.evaluate_state(state)

            max_value = -float('inf')
            
            for direction, next_tile in self.valid_moves(state.player_tile):
                
                next_state = self.apply_pacman_move(state, next_tile)

                score = self.minimax(next_state, depth, ghost_index=1)
                max_value = max(max_value, score)
                
            return max_value

        else:
            current_ghost_index = ghost_index - 1 
            min_value = float('inf')
            
            current_ghost_tile = state.ghost_tiles[current_ghost_index]
            
            for direction, next_tile in self.valid_moves(current_ghost_tile): 
                next_state = self.apply_ghost_move(state, current_ghost_index, next_tile)
                
                if ghost_index == len(state.ghost_tiles):
                    next_ghost_index = 0
                    next_depth = depth - 1
                else:
                    next_ghost_index = ghost_index + 1
                    next_depth = depth

                score = self.minimax(next_state, next_depth, next_ghost_index)
                min_value = min(min_value, score)
                
            return min_value

    def choose_minimax_move(self, current_game_state, search_depth=3):
        
        best_score = -float('inf')
        best_move_direction = self.direction 
 
        for direction, next_tile in self.valid_moves(current_game_state.player_tile):
            
            next_state = self.apply_pacman_move(current_game_state, next_tile)
            
            score = self.minimax(next_state, search_depth, ghost_index=1) 
            
            if score > best_score:
                best_score = score
                best_move_direction = direction
            
            elif score == best_score and direction == self.direction:
                best_move_direction = direction
                
        return best_move_direction

    def check_for_ghosts(self, ghosts_group, sense_radius_tiles=4):
        sense_radius_pixels = sense_radius_tiles * TILE_SIZE
        
        nearby_ghosts = []
        
        for ghost in ghosts_group:
            distance_squared = (self.rect.centerx - ghost.rect.centerx)**2 + \
                               (self.rect.centery - ghost.rect.centery)**2
            
            if distance_squared < sense_radius_pixels**2:
                nearby_ghosts.append(ghost)
                
        return nearby_ghosts

    def find_next_best_move(self, pellets_group, energizers_group, ghosts_group, player_mode):
        current_tile = self.get_tile()
        possible_moves = self.valid_moves(current_tile)
        best_score = -float('inf')
        best_direction = self.direction 
        
        all_food_tiles = list((p.rect.centerx // TILE_SIZE, p.rect.centery // TILE_SIZE) for p in pellets_group)
        all_food_tiles.extend(list((e.rect.centerx // TILE_SIZE, e.rect.centery // TILE_SIZE) for e in energizers_group))

        if not possible_moves:
            return best_direction

        for direction, next_tile in possible_moves:
            score = 0
            
            min_dist_to_food = float('inf')
            if all_food_tiles:
                for food_tile in all_food_tiles:
                    dist = self.hmd(next_tile, food_tile) 
                    min_dist_to_food = min(min_dist_to_food, dist)
                
                if min_dist_to_food != float('inf'):
                    score += 5000 / (min_dist_to_food + 1)  

            if next_tile in all_food_tiles:
                score += 10000 
                
            if self._is_ghost_nearby(next_tile, ghosts_group, player_mode):
                score -= 20000
            if direction == (-self.direction[0], -self.direction[1]):
                score -= 100 
            
            elif direction == self.direction:
                score += 50 

            if score > best_score:
                best_score = score
                best_direction = direction
            
            elif score == best_score and direction == self.direction:
                 best_direction = direction
                 
        return best_direction

    def apply_pacman_move(self, state, next_tile: tuple) -> 'SimulatedState':
        new_player_tile = next_tile

        new_pellets = state.pellets_left.copy()
        new_energizers = state.energizers_left.copy()
        
        if next_tile in new_pellets:
            new_pellets.remove(next_tile)
        elif next_tile in new_energizers:
            new_energizers.remove(next_tile)
 
        return SimulatedState(new_player_tile, state.ghost_tiles, state.maze, new_pellets, new_energizers)

    def apply_ghost_move(self, state, ghost_index, next_tile: tuple) -> 'SimulatedState':

        new_ghost_tiles = list(state.ghost_tiles)
        new_ghost_tiles[ghost_index] = next_tile

        return SimulatedState(state.player_tile, tuple(new_ghost_tiles), state.maze, state.pellets_left, state.energizers_left)

    def evaluate_state(self, state: 'SimulatedState'):
        score = 0
        score -= (len(state.pellets_left) * 100) 
        score -= (len(state.energizers_left) * 500) 

        if state.pellets_left or state.energizers_left:
            all_food_tiles = list(state.pellets_left) + list(state.energizers_left)
            min_food_dist = float('inf')
            
            for food_tile in all_food_tiles:
                dist = self.hmd(state.player_tile, food_tile)
                min_food_dist = min(min_food_dist, dist)

            score += 5000 / (min_food_dist + 1)
            
        min_ghost_dist = float('inf')
        for ghost_tile in state.ghost_tiles:
            dist = self.hmd(state.player_tile, ghost_tile) 
            min_ghost_dist = min(min_ghost_dist, dist)
            
        if min_ghost_dist < 8:
            score -= (8 - min_ghost_dist)**3 * 10 
        
        return score

    def get_current_simulated_state(self, ghosts_group, pellets_group, energizers_group):
        player_tile = self.get_tile()
        
        ghost_tiles = tuple(ghost.get_tile() for ghost in ghosts_group)
        
        pellets_left = set((p.rect.centerx // TILE_SIZE, p.rect.centery // TILE_SIZE) for p in pellets_group)
        energizers_left = set((e.rect.centerx // TILE_SIZE, e.rect.centery // TILE_SIZE) for e in energizers_group)
        
        return SimulatedState(player_tile, ghost_tiles, self.maze, pellets_left, energizers_left)

    def auto_update(self, keys_pressed, walls, pellets_group, energizers_group, ghosts_group, player_mode):
 
        current_time = pygame.time.get_ticks()
        if self.invincible:
            if current_time - self.invincible_timer > self.invincible_duration:
                self.invincible = False
                self.visible = True
            else: 
                if current_time - self.blink_timer > 100:
                    self.visible = not self.visible
                    self.blink_timer = current_time
        if not self.visible and self.invincible:
            pass
        next_direction = self.direction
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
        
        if self.at_tile_center():
            if player_mode == "reflex":
                next_direction = self.find_next_best_move(pellets_group, energizers_group, ghosts_group, player_mode)
            elif player_mode == "minimax":
                current_state = self.get_current_simulated_state(ghosts_group, pellets_group, energizers_group)
                next_direction = self.choose_minimax_move(current_state, search_depth=2)
            elif player_mode == "alphabeta":
                current_state = self.get_current_simulated_state(ghosts_group, pellets_group, energizers_group)
                next_direction = self.choose_alphabeta_move(current_state, search_depth=3)

            self.set_direction(next_direction)

        
        dir_x, dir_y = self.direction
        dx = dir_x * self.speed
        dy = dir_y * self.speed
        
        self.rect.x += dx
        collided_walls = pygame.sprite.spritecollide(self, walls, False)
        
        if collided_walls:
            for wall in collided_walls:
                if dx > 0:
                    self.rect.right = wall.rect.left
                elif dx < 0: 
                    self.rect.left = wall.rect.right
            dx = 0
            self.rect.centery = (self.rect.centery // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2
            
        self.rect.y += dy
        collided_walls = pygame.sprite.spritecollide(self, walls, False) 

        if collided_walls:
            for wall in collided_walls:
                if dy > 0: 
                    self.rect.bottom = wall.rect.top
                elif dy < 0:
                    self.rect.top = wall.rect.bottom
            self.rect.centerx = (self.rect.centerx // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2

        if dx != 0 or dy != 0:
            if self.mouth_opening:
                self.mouth_angle += self.mouth_speed
                if self.mouth_angle >= 30:
                    self.mouth_angle = 30
                    self.mouth_opening = False
            else:
                self.mouth_angle -= self.mouth_speed
                if self.mouth_angle <= 0:
                    self.mouth_angle = 0
                    self.mouth_opening = True
        else:
            self.mouth_angle = 0 

        self.redraw()
                
    def alphabeta(self, state: SimulatedState, depth, alpha, beta, ghost_index):
        if state.is_terminal() or depth == 0:
         return self.evaluate_state(state)

    #max layer pacman
        if ghost_index == 0:
            value = -float('inf')

        for direction, next_tile in self.valid_moves(state.player_tile):
            next_state = self.apply_pacman_move(state, next_tile)
            score = self.alphabeta(next_state, depth, alpha, beta, ghost_index=1)
            value = max(value, score)
            alpha = max(alpha, value)

            if alpha >= beta:
                break  # prune

        return value


    #min layers ghosts
        ghost_i = ghost_index - 1
        value = float('inf')
        current_ghost_tile = state.ghost_tiles[ghost_i]

        for direction, next_tile in self.valid_moves(current_ghost_tile):
            next_state = self.apply_ghost_move(state, ghost_i, next_tile)

            if ghost_index == len(state.ghost_tiles):
                next_gi = 0
                next_depth = depth - 1
            else:
                next_gi = ghost_index + 1
                next_depth = depth

            score = self.alphabeta(next_state, next_depth, alpha, beta, next_gi)
            value = min(value, score)
            beta = min(beta, value)

            if beta <= alpha:
                break  # prune

        return value
    
    def choose_alphabeta_move(self, current_game_state, search_depth=3):
        best_score = -float('inf')
        best_direction = self.direction

        for direction, next_tile in self.valid_moves(current_game_state.player_tile):
            next_state = self.apply_pacman_move(current_game_state, next_tile)

            score = self.alphabeta(next_state, search_depth,
                               alpha=-float('inf'),
                               beta=float('inf'),
                               ghost_index=1)

            if score > best_score:
                best_score = score
                best_direction = direction

            elif score == best_score and direction == self.direction:
                best_direction = direction

        return best_direction

            