# These are the shared defaults for every Pong difficulty.

from src.core.difficulty_base import Difficulty

class PongDifficulty(Difficulty):
    # -- ball --
    ball_base_speed = 8     # matches the original TOTAL_SPEED constant
    randomise_ball = False  # randomise the serve angle instead of the same one every time
    speed_up_on_hit = False # +speed_up_amount to the ball every paddle hit
    speed_up_amount = 1     # reset_ball() (called on every score) brings it back to base_speed
   
    # -- player --
    paddle_speed = 8

    # -- AI (Pong2PMode never reads these, there's no self.ai over there) --
    ai_speed = 7             # paddle's max px/frame
    ai_predictive = False    # False = chase the ball's current y (Basic AI)
                              # True  = predict where the ball will actually be
    ai_error = 0              # px of random misjudgement mixed into the prediction,
                              # so a predictive AI isn't a perfect wall