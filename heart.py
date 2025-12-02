import pygame

def heart(surface, lives, x, y, size=25, color=(255, 0, 0)):
    r = int(size * 0.28)
    
    for i in range(lives):
        cx = x + i * (size + 10)
        cy = y

        pygame.draw.circle(surface, color, (cx + r, cy + r), r)
        pygame.draw.circle(surface, color, (cx + size - r, cy + r), r)

        pygame.draw.polygon(surface, color, [
            (cx, cy + r),
            (cx + size, cy + r),
            (cx + size // 2, cy + size + r)
        ])
