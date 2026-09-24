

# Simple paddle AI that tracks the ball with humanised speed caps
# Speed parameter makes it react faster/slower for difficulty tuning
#
# Two modes now instead of one:
#  - Basic  (predictive=False): chases the ball's CURRENT y. This is
#    the original behaviour, untouched - Classic and Advanced both use it.
#  - Predictive (predictive=True): works out where the ball will
#    actually BE by the time it reaches the paddle (bouncing it off the
#    top/bottom walls in the maths, same as light off a mirror), and
#    chases that instead. Used by Hell.
#
# error adds a few px of random wobble to the predictive target so it's
# not a perfect wall - combined with the speed cap, a sharp enough shot
# still gets through.

import pygame
import random

class AI:
    def __init__(self, speed=7, predictive=False, error=0):
        self.speed = speed
        self.predictive = predictive
        self.error = error

    def move(self, paddle, ball, ball_speed_x=0, ball_speed_y=0, screen_height=None):
        # Move the AI paddle toward wherever it thinks the ball is headed
        target_y = self._get_target_y(paddle, ball, ball_speed_x, ball_speed_y, screen_height)

        if paddle.centery < target_y:
            paddle.y += self.speed
        elif paddle.centery > target_y:
            paddle.y -= self.speed

    def _get_target_y(self, paddle, ball, ball_speed_x, ball_speed_y, screen_height):
        if not self.predictive or ball_speed_x == 0 or not screen_height:
            # Basic AI - just chase the ball's current position
            return ball.centery

        moving_towards_us = (ball_speed_x > 0) == (paddle.centerx > ball.centerx)
        if not moving_towards_us:
            # ball's heading away from us... that's ok, just, drift back to the middle
            # so we're not already glued in place when it turns back around
            return screen_height // 2

        # how many frames until the ball reaches our x position, and where
        # would it be by then if nothing was in the way
        distance_x = abs(paddle.centerx - ball.centerx)
        frames = distance_x / max(1, abs(ball_speed_x))
        predicted_y = ball.centery + ball_speed_y * frames

        # reflect the prediction off the top/bottom walls (unfold-and-fold
        # trick. I guess it's the same idea as light bouncing off a mirror 😅) so it still
        # works even if the ball's going to bounce once or twice more
        # before it gets here
        predicted_y = predicted_y % (2 * screen_height)
        if predicted_y > screen_height:
            predicted_y = 2 * screen_height - predicted_y

        if self.error:
            predicted_y += random.uniform(-self.error, self.error)

        return predicted_y
