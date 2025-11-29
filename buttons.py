import pygame
from settings import WHITE, BLACK

class Button:
    def __init__(self, x, y, width, height, text, font, callback,bg_color=(100,100,100), hover_color=(150,150,150)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.callback = callback
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.hovered = False

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect)
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                self.callback()