from src.games.pong.difficulties._base import PongDifficulty

class Difficulty(PongDifficulty):
    name = "Classic"
    description = "Basic AI, steady ball speed"
    TOTAL_SPEED = 9
    ai_error = 50
    ai_speed = 6
    paddle_speed = 8