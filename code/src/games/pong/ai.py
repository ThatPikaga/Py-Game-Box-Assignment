


# Simple paddle AI that tracks the ball with humanised speed caps
# Speed parameter makes it react faster/slower for difficulty tuning

import pygame

class AI:
    def __init__(self, speed=7):
        self.speed = speed
        self.reaction_delay = 0

    def move(self, paddle, ball):
        # Move the AI paddle toward the ball's Y position
        if paddle.centery < ball.centery:
            paddle.y += self.speed
        elif paddle.centery > ball.centery:
            paddle.y -= self.speed
