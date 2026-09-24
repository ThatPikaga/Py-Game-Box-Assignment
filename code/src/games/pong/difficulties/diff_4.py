from src.games.pong.difficulties._base import PongDifficulty

class Difficulty(PongDifficulty):
    name = "I am Death Incarnate"
    description = "|||[ (°…°) ]|||"
    ball_base_speed = 16
    randomise_ball = True
    speed_up_on_hit = True
    speed_up_amount = 3
    ai_speed = 12
    ai_predictive = True
    ai_error = 10
    paddle_speed = 14
