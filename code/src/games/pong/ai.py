class AI:
    def __init__(self, speed=5):
        self.speed = speed

    def move(self, paddle, ball):
        # Track the center of the ball
        if paddle.centery < ball.centery:
            paddle.y += self.speed
        elif paddle.centery > ball.centery:
            paddle.y -= self.speed
