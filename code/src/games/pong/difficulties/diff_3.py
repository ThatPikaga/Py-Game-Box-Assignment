from src.games.pong.difficulties._base import PongDifficulty

class Difficulty(PongDifficulty):
    name = """Hell"""
    description = "Ball speeds up on every hit. The game can See Y°u"
    ball_base_speed = 9
    randomise_ball = True
    speed_up_on_hit = True
    speed_up_amount = 1
    ai_speed = 9
    ai_predictive = True
    ai_error = 250
    paddle_speed = 9
