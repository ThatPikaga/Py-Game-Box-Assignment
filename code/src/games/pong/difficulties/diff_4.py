from src.games.pong.difficulties._base import PongDifficulty

class Difficulty(PongDifficulty):
    name = "I am Death Incarnate"
    description = "|||[ (°…°) ]|||"
    ball_base_speed = 3
    randomise_ball = True
    speed_up_on_hit = True
    speed_up_amount = 3
    ai_speed = 10
    ai_predictive = True
    ai_error = 5
    paddle_speed = 14
