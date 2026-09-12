


# ========================[ P O N G   —   C O M M O N ]==============================
# Shared constants, base mode, and helpers for all Pong modes.
# Instead of duplicating ball physics, paddle handling, and drawing
# across mode_ai.py and mode_2p.py, we put it all here.

import pygame
import math as maths
from src.core.game_base import GameBase
from src.core.constants import *
from src.engine.input_handler import GameKeyHandler

# == Ball / Paddle helpers ============================================

def make_paddle_rect(x_center, y_center=None):
    """Create a left-side paddle rect (y centred by default)."""
    if y_center is None:
        y_center = SCREEN_HEIGHT // 2
    return pygame.Rect(x_center, y_center - PONG_PADDLE_H // 2,
                        PONG_PADDLE_W, PONG_PADDLE_H)


def make_paddle_rect_right():
    """Create a right-side paddle rect, y centred."""
    return pygame.Rect(SCREEN_WIDTH - 50 - PONG_PADDLE_W,
                        SCREEN_HEIGHT // 2 - PONG_PADDLE_H // 2,
                        PONG_PADDLE_W, PONG_PADDLE_H)


def make_ball_rect():
    return pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2,
                        SCREEN_HEIGHT // 2 - BALL_SIZE // 2,
                        BALL_SIZE, BALL_SIZE)


def reset_ball(ball, ball_speed_x, ball_speed_y):
    """Centre the ball and flip horizontal direction."""
    ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    ball_speed_x = -ball_speed_x if ball_speed_x > 0 else ball_speed_x
    ball_speed_y = 5 if ball_speed_y > 0 else -5
    return ball_speed_x, ball_speed_y


# == Physics helpers ==================================================

def wall_bounce(ball, ball_speed_x, ball_speed_y):
    """Bounce off top/bottom walls. Returns updated ball_speed_y."""
    if ball.top <= 0 or ball.bottom >= SCREEN_HEIGHT:
        ball_speed_y *= -1
        if ball.top <= 0:
            ball.top = 0
        else:
            ball.bottom = SCREEN_HEIGHT
    return ball_speed_y


def paddle_bounce(ball, paddle, ball_speed_x, ball_speed_y):
    """
    Calculate bounce angle off a paddle.
    Returns (ball_speed_x, ball_speed_y) after the bounce.
    The return ball_speed_x is positive for left-paddle hits and
    negative for right-paddle hits — the caller should reverse sign
    if the paddle is on the right side.
    """
    pc = paddle.centery
    bc = ball.centery
    ri = bc - pc
    ni = ri / (PONG_PADDLE_H / 2)
    ni = max(-0.9, min(0.9, ni))
    new_ball_speed_y = ni * BOUNCE_SPEED
    new_ball_speed_x = maths.sqrt(max(0, TOTAL_SPEED**2 - new_ball_speed_y**2))
    return new_ball_speed_x, new_ball_speed_y


# == Drawing helpers ==================================================

def draw_pong_board(surface, p1_rect, p2_rect, ball_rect,
                    p1_score, p2_score,
                    p1_colour=COL_PLAYER, p2_colour=COL_AI,
                    ball_colour=COL_WHITE,
                    font_big=None, font_body=None):
    """Draw the full pong playfield with scores."""
    if font_big is None:
        font_big = pygame.font.Font(None, FONT_TITLE_SIZE)
    if font_body is None:
        font_body = pygame.font.Font(None, FONT_BODY_SIZE)

    surface.fill(COL_BLACK)

    # paddles
    pygame.draw.rect(surface, p1_colour, p1_rect)
    pygame.draw.rect(surface, p2_colour, p2_rect)

    # ball
    pygame.draw.ellipse(surface, ball_colour, ball_rect)

    # centre line
    pygame.draw.aaline(surface, COL_WHITE,
                       (SCREEN_WIDTH // 2, 0),
                       (SCREEN_WIDTH // 2, SCREEN_HEIGHT))

    # scores
    p1t = font_big.render(str(p1_score), True, p1_colour)
    surface.blit(p1t, (SCREEN_WIDTH // 4, 20))
    p2t = font_big.render(str(p2_score), True, p2_colour)
    surface.blit(p2t, (3 * SCREEN_WIDTH // 4, 20))


# == Base Mode =========================================================

class PongBaseMode(GameBase):
    """
    Shared base for all Pong game modes.
    
    Subclasses must set:
      - self.name (e.g. "Pong 2 Players")
      - self.p1 / self.player / self.paddle_left (left paddle rect)
      - self.p2 / self.opponent / self.paddle_right (right paddle rect)
      - self.ball
      - self.ball_speed_x, self.ball_speed_y
      - self.input (or self.p1_input / self.p2_input for 2P mode)
      - self.score_left / self.score_p1 / self.player_score
      - self.score_right / self.score_p2 / self.opponent_score
    
    And override _handle_left_input() and _handle_right_input() for
    movement.
    """

    def __init__(self):
        super().__init__()
        self.font_big = pygame.font.Font(None, FONT_TITLE_SIZE)
        self.font_body = pygame.font.Font(None, FONT_BODY_SIZE)

    # == shared update logic ==

    def _update_ball(self):
        """Move the ball and handle wall/paddle collisions."""
        self.ball.x += self.ball_speed_x
        self.ball.y += self.ball_speed_y

        # top/bottom wall bounce
        self.ball_speed_y = wall_bounce(self.ball, self.ball_speed_x, self.ball_speed_y)

    def _check_paddle_hit_left(self, paddle):
        """Player/left-paddle collision. Updates ball speed in-place."""
        if self.ball.colliderect(paddle) and self.ball_speed_x <= 0:
            self.ball_speed_x, self.ball_speed_y = paddle_bounce(
                self.ball, paddle, self.ball_speed_x, self.ball_speed_y,
            )
            # left paddle = positive x direction
            self.ball_speed_x = abs(self.ball_speed_x)

    def _check_paddle_hit_right(self, paddle):
        """AI/right-paddle collision. Updates ball speed in-place."""
        if self.ball.colliderect(paddle) and self.ball_speed_x >= 0:
            self.ball_speed_x, self.ball_speed_y = paddle_bounce(
                self.ball, paddle, self.ball_speed_x, self.ball_speed_y,
            )
            # right paddle = negative x direction
            self.ball_speed_x = -abs(self.ball_speed_x)

    def _check_scoring(self):
        """Check if ball went past left/right edges. Returns True if scored."""
        scored = False
        if self.ball.left <= 0:
            self._on_right_scored()
            self.reset_ball()
            scored = True
        if self.ball.right >= SCREEN_WIDTH:
            self._on_left_scored()
            self.reset_ball()
            scored = True
        return scored

    def _on_left_scored(self):
        """Called when left-side player scores. Override in subclass."""
        pass

    def _on_right_scored(self):
        """Called when right-side player scores. Override in subclass."""
        pass

    def reset_ball(self):
        """Centre ball and flip direction. Subclass should call this."""
        self.ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.ball_speed_x = -self.ball_speed_x if self.ball_speed_x > 0 else self.ball_speed_x
        self.ball_speed_y = 5 if self.ball_speed_y > 0 else -5

    # == shared submit / cleanup ==

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.pause_requested = True
        return None

    def cleanup(self):
        pass