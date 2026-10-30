import pygame
import random
from src.core.constants import scale_size

class PowerUp(pygame.Rect):
    def __init__(self, x, y, type_str):
        super().__init__(x, y, scale_size(25), scale_size(15))
        self.type = type_str
        self.speed = scale_size(3)

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        colour = (0, 255, 0)
        if self.type == 'EXPAND':
            colour = (0, 255, 0)
        elif self.type == 'SHRINK':
            colour = (255, 0, 0)
        elif self.type == 'SLOW':
            colour = (0, 0, 255)
        elif self.type == 'FAST':
            colour = (255, 255, 0)
        pygame.draw.rect(screen, colour, self)
