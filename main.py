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
from buttons import Button

walls_group = pygame.sprite.Group()
pellets_group = pygame.sprite.Group()
energizers_group = pygame.sprite.Group()

points = 0

def draw_path(surface, path, color=(0, 255, 0)):
    for (tx, ty) in path:
        rect = pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, color, rect, 2)


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


player = Player(3 * TILE_SIZE, 3 * TILE_SIZE)
player_group = pygame.sprite.Group(player)


ghost_group = pygame.sprite.Group()

ghost_group.add(Ghost(8 * TILE_SIZE, 7 * TILE_SIZE, MAZE, BLINKY))     
ghost_group.add(Ghost(10 * TILE_SIZE, 7 * TILE_SIZE, MAZE, PINKY))  
ghost_group.add(Ghost(13 * TILE_SIZE, 7 * TILE_SIZE, MAZE, INKY))  
ghost_group.add(Ghost(14 * TILE_SIZE, 7 * TILE_SIZE, MAZE, CLYDE)) 

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

panel.add_button("DFS", set_dfs)
panel.add_button("BFS", set_bfs)
panel.add_button("A*", set_astar)
panel.add_button("Random", set_random)

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

    keys = pygame.key.get_pressed()

    player.update(keys, walls_group)

    collided_ghosts = pygame.sprite.spritecollide(player, ghost_group, False)
    for ghost in collided_ghosts:
        if ghost.frightened:
            points += 200
            ghost.reset_position()
            print("Ghost eaten! +200")
        else:
            points -= 500
            if points < 0:
                print("Pac-Man caught! GAME OVER")
                running = False

    for ghost in ghost_group:
        ghost.update(player, mode=ghost_mode)  

    screen.fill(BLACK)

    walls_group.draw(screen)
    pellets_group.draw(screen) 
    energizers_group.draw(screen)
    player_group.draw(screen)
    ghost_group.draw(screen)
    panel.draw(screen)
    score_text = font.render(f"Points: {points}", True, (255, 255, 255))
    screen.blit(score_text, (SCREEN_WIDTH - 140, 50))

    if show_paths:
        for ghost in ghost_group:
            start = ghost.get_tile()
            player_tile = (
                player.rect.centerx // TILE_SIZE,
                player.rect.centery // TILE_SIZE
            )

            if ghost_mode == "bfs":
                path = ghost.bfs_full_path(start, player_tile)
                draw_path(screen, path, (0, 255, 0))


            elif ghost_mode == "dfs":
                path = ghost.dfs_full_path(start, player_tile)
                draw_path(screen, path, (255, 255, 0))

            elif ghost_mode == "astar":
                path = ghost.astar_full_path(start, player_tile)
                draw_path(screen, path, (255, 0, 0))

    pygame.display.flip()


pygame.quit()
sys.exit()
