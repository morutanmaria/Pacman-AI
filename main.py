import pygame
import sys

from settings import *
from player import Player
from ghost import Ghost
from level import MAZE   

MAZE_WIDTH = len(MAZE[0]) * TILE_SIZE
MAZE_HEIGHT = len(MAZE) * TILE_SIZE

SCREEN_WIDTH = MAZE_WIDTH + 150 
SCREEN_HEIGHT = MAZE_HEIGHT

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man with Ghost AI")

clock = pygame.time.Clock()


from wall import Wall
from pellet import Pellet 
from energizer import Energizer
from buttonPanel import ButtonPanel
from cherry import Cherry
from buttons import Button
from heart import heart

walls_group = pygame.sprite.Group()
pellets_group = pygame.sprite.Group()
energizers_group = pygame.sprite.Group()
cherries_group = pygame.sprite.Group()

points = 0
lives = 3 

# cherry spawn logic
CHERRY_THRESHOLDS = [70, 170]
cherry_spawned_flags = {t: False for t in CHERRY_THRESHOLDS}
cherry_active = False
cherry_spawn_time = None   #cand apare (ms)
CHERRY_DURATION = 8000   # 8 secunde
CHERRY_SCORE = 100

GHOST_HOUSE_ROWS = range(9, 13)
GHOST_HOUSE_COLS = range(10, 20)

def draw_path(surface, path, color=(0, 255, 0)):
    for (tx, ty) in path:
        rect = pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, color, rect, 2)

def spawn_cherry_under_house():
    spawn_row = max(GHOST_HOUSE_ROWS) + 1
    spawn_col = (min(GHOST_HOUSE_COLS) + max(GHOST_HOUSE_COLS)) // 2

    x = spawn_col * TILE_SIZE + TILE_SIZE // 2
    y = spawn_row * TILE_SIZE + TILE_SIZE // 2

    cherry = Cherry(x, y)
    return cherry


for row_idx, row in enumerate(MAZE):
    for col_idx, tile in enumerate(row):
        if tile == 1:  
            wall = Wall(
                col_idx * TILE_SIZE,
                row_idx * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
            walls_group.add(wall)
        elif tile == 0:
                pellet = Pellet(
                    col_idx * TILE_SIZE + TILE_SIZE//2,
                    row_idx * TILE_SIZE + TILE_SIZE//2
                )
                pellets_group.add(pellet)
        elif tile == 2:
            energizer = Energizer(
                col_idx * TILE_SIZE + TILE_SIZE//2,
                row_idx * TILE_SIZE + TILE_SIZE//2
            )
            energizers_group.add(energizer)


player = Player(14 * TILE_SIZE, 14 * TILE_SIZE, MAZE)
player_group = pygame.sprite.Group(player)
player_mode = "manual"

ghost_group = pygame.sprite.Group()

ghost_group.add(Ghost(12 * TILE_SIZE, 10 * TILE_SIZE, MAZE, BLINKY, "blinky"))     
ghost_group.add(Ghost(16 * TILE_SIZE, 10 * TILE_SIZE, MAZE, PINKY, "pinky"))  
ghost_group.add(Ghost(12 * TILE_SIZE, 9 * TILE_SIZE, MAZE, INKY, "inky"))  
ghost_group.add(Ghost(16* TILE_SIZE, 9 * TILE_SIZE, MAZE, CLYDE, "clyde")) 

for ghost in ghost_group:
    ghost.set_walls(walls_group)

font = pygame.font.SysFont(None, 24)
panel = ButtonPanel(SCREEN_WIDTH - 150, 100, 120, 40, 10, font)

ghost_mode = "random"
show_paths= False
def set_dfs():
    global ghost_mode
    ghost_mode = "dfs"
def set_bfs():
    global ghost_mode
    ghost_mode = "bfs"
def set_astar():
    global ghost_mode
    ghost_mode = "astar"
def set_random():
    global ghost_mode
    ghost_mode = "random"
def set_reflex():
    global player_mode
    player_mode = "reflex"
def set_minimax():
    global player_mode
    player_mode = "minimax"
def set_manual():
    global player_mode
    player_mode = "manual"

panel.add_button("DFS", set_dfs)
panel.add_button("BFS", set_bfs)
panel.add_button("A*", set_astar)
panel.add_button("Random", set_random)
panel.add_button("Manual", set_manual)
panel.add_button("Reflex", set_reflex)
panel.add_button("Minimax", set_minimax)
#panel.add_button("AlphaBeta", set_alphabeta)

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        panel.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                show_paths = not show_paths
                print("Show paths:", show_paths)

    eaten_energizer = pygame.sprite.spritecollide(player, energizers_group, True)
    if eaten_energizer:
        print("Yummy! Ghosts are now frightened!")
        points += 50
        for ghost in ghost_group:
            ghost.set_frightened_mode()

    eaten_pellet = pygame.sprite.spritecollide(player, pellets_group, True)
    if eaten_pellet:
        points += 10
        print("Yum! Pretty good")

    eaten_cherry = pygame.sprite.spritecollide(player, cherries_group, True)
    if eaten_cherry:
        points += CHERRY_SCORE
        cherry_active = False
        cherry_spawn_time = None
        print("Cherry eaten! +100")

    keys = pygame.key.get_pressed()

    if player_mode == "manual":
        player.update(keys, walls_group)
    else:
        player.auto_update(walls_group, pellets_group, energizers_group, ghost_group, player_mode)

    current_time = pygame.time.get_ticks()

    #apare cherry la prag (doar o data apare cand atingi pragul intr-un meci)
    #apare doar daca nu este alt cherry deja pe harta
    for t in CHERRY_THRESHOLDS:
        if points >= t and not cherry_spawned_flags[t] and not cherry_active:
            cherry = spawn_cherry_under_house()
            cherries_group.add(cherry)
            cherry_active = True
            cherry_spawn_time = pygame.time.get_ticks()
            cherry_spawned_flags[t] = True
            break

    #stergem dupa 8 secunde
    if cherry_active and cherry_spawn_time is not None:
        if pygame.time.get_ticks() - cherry_spawn_time > CHERRY_DURATION:
            for c in list(cherries_group):
                c.kill()
            cherry_active = False
            cherry_spawn_time = None

    if not player.invincible:
        collided_ghosts = pygame.sprite.spritecollide(player, ghost_group, False)
        
        if collided_ghosts:
            for ghost in collided_ghosts:
                if hasattr(ghost, 'frightened') and ghost.frightened:
                    points += 200
                    ghost.eaten = True
                    print("Ghost eaten! +200")
                else:
                    points -= 500
                    lives -= 1
                    ghost.reset_position()
                    if points < 0:
                        points = 0
                    if lives == 0:
                        lost_font = pygame.font.SysFont(None, 35)  

                        lost_text = lost_font.render("YOU LOST!", True, (255, 255, 0))

                        text_x = SCREEN_WIDTH - 150 + 15
                        text_y = 470  

                        screen.blit(lost_text, (text_x, text_y))
                        pygame.display.flip()
                        pygame.time.wait(3000)
                        running = False
                    
                    player.invincible = True
                    player.invincible_timer = current_time
                    player.blink_timer = current_time
                    
                    player.rect.x = 13 * TILE_SIZE
                    player.rect.y = 13 * TILE_SIZE
                    
                    break

    for ghost in ghost_group:
        ghost.update(player, mode=ghost_mode)  

    screen.fill(BLACK)

    walls_group.draw(screen)
    pellets_group.draw(screen)
    cherries_group.draw(screen)
    energizers_group.draw(screen)
    player_group.draw(screen)
    ghost_group.draw(screen)
    panel.draw(screen)
    score_text = font.render(f"Points: {points}", True, (255, 255, 255))
    screen.blit(score_text, (SCREEN_WIDTH - 140, 50))
    heart(screen, lives, SCREEN_WIDTH - 140, 10, size=20)

    if show_paths:
        for ghost in ghost_group:
            start = ghost.get_tile()
            player_tile = (
                player.rect.centerx // TILE_SIZE,
                player.rect.centery // TILE_SIZE
            )

            ghost_color = ghost.color

            if ghost_mode == "bfs":
                path = ghost.bfs_full_path(start, player_tile)
                draw_path(screen, path, ghost_color)

            elif ghost_mode == "dfs":
                path = ghost.dfs_full_path(start, player_tile)
                draw_path(screen, path, ghost_color)

            elif ghost_mode == "astar":
                path = ghost.astar_full_path(start, player_tile)
                draw_path(screen, path, ghost_color)

    pygame.display.flip()

    if len(pellets_group) == 0 and len(energizers_group) == 0:
        win_font = pygame.font.SysFont(None, 35)  

        win_text = win_font.render("YOU WIN!", True, (255, 255, 0))

        text_x = SCREEN_WIDTH - 150 + 15
        text_y = 470  

        screen.blit(win_text, (text_x, text_y))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False

pygame.quit()
sys.exit()
