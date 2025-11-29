import pygame
import sys

from settings import *
from player import Player
from ghost import Ghost
from level import MAZE   

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man with Ghost AI")

clock = pygame.time.Clock()


from wall import Wall

walls_group = pygame.sprite.Group()

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



player = Player(2 * TILE_SIZE, 2 * TILE_SIZE)
player_group = pygame.sprite.Group(player)


ghost_group = pygame.sprite.Group()

ghost_group.add(Ghost(7 * TILE_SIZE, 7 * TILE_SIZE, MAZE, color=(255, 0, 0)))     
ghost_group.add(Ghost(10 * TILE_SIZE, 7 * TILE_SIZE, MAZE, color=(0, 255, 255)))  
ghost_group.add(Ghost(13 * TILE_SIZE, 7 * TILE_SIZE, MAZE, color=(255, 128, 0)))  


running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    player.update(keys, walls_group)

    for ghost in ghost_group:
        ghost.update(player, mode="random")  


    screen.fill(BLACK)

    walls_group.draw(screen)
    player_group.draw(screen)
    ghost_group.draw(screen)

    pygame.display.flip()


pygame.quit()
sys.exit()
