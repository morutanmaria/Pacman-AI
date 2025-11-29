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
panel = ButtonPanel(SCREEN_WIDTH - 150, 50, 120, 40, 10, font)

ghost_mode = "random"
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

    keys = pygame.key.get_pressed()

    player.update(keys, walls_group)

    for ghost in ghost_group:
        ghost.update(player, mode=ghost_mode)  

    screen.fill(BLACK)

    walls_group.draw(screen)
    pellets_group.draw(screen) 
    energizers_group.draw(screen)
    player_group.draw(screen)
    ghost_group.draw(screen)
    panel.draw(screen)

    pygame.display.flip()


pygame.quit()
sys.exit()
