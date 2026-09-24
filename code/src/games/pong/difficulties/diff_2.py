# Same Basic AI as Classic - the jump in difficulty here is entirely
# the ball: it starts faster, and the serve angle is randomised each
# time instead of the same gentle angle every single serve.

from src.games.pong.difficulties._base import PongDifficulty

class Difficulty(PongDifficulty):
    name = "Advanced"
    description = "The ball is faster and less predictable."
    ball_base_speed = 10
    randomise_ball = True
    paddle_speed = 9
