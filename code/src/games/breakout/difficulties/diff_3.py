from ._base import BreakoutDifficulty


class Difficulty(BreakoutDifficulty):
    name = "I will Break You"
    description = "One Life to break them all."
    lives = 2
    paddle_speed = 9
    ball_speed = 14
