from ._base import BreakoutDifficulty


class Difficulty(BreakoutDifficulty):
    name = "Medium"
    description = "A standard game of Breakout."
    lives = 3
    paddle_speed = 9
    ball_speed = 8
