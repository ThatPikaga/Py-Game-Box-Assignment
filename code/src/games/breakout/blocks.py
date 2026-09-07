import pygame
import random

class Brick(pygame.Rect):
    def __init__(self, x, y, width, height, colour, points):
        super().__init__(x, y, width, height)
        self.colour = colour
        self.points = points
        self.alive = True

def create_grid(rows, cols, width, height, offset_top=60, padding=4):
    bricks = []
    colours = [
        (255, 0, 0),     # Red
        (255, 165, 0),   # Orange
        (255, 255, 0),   # Yellow
        (0, 255, 0),     # Green
        (0, 0, 255),     # Blue
        (128, 0, 128)    # Purple
    ]
    
    for row in range(rows):
        colour = colours[row % len(colours)]
        points = (rows - row) * 10
        for col in range(cols):
            x = col * (width + padding) + padding
            y = row * (height + padding) + offset_top
            bricks.append(Brick(x, y, width, height, colour, points))
    return bricks
