# ========================[ P O N G   —   C O M M O N ]==============================
# Shared constants, base mode, and helpers for all Pong modes.
# Instead of duplicating ball physics, paddle handling, and drawing
# across mode_ai.py and mode_2p.py, we put it all here.

import pygame
import math as maths
import random
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


def paddle_bounce(ball, paddle, ball_speed_x, ball_speed_y, total_speed=TOTAL_SPEED, bounce_speed=None):
    """
    Calculate bounce angle off a paddle.
    Returns (ball_speed_x, ball_speed_y) after the bounce.
    The return ball_speed_x is positive for left-paddle hits and
    negative for right-paddle hits — the caller should reverse sign
    if the paddle is on the right side.

    total_speed/bounce_speed let a difficulty-aware caller control how
    fast the ball leaves the paddle (e.g. Hell mode ramping the ball up
    every hit) - default is the shared TOTAL_SPEED/BOUNCE_SPEED from
    constants.py, exactly like before.
    """
    if bounce_speed is None:
        bounce_speed = total_speed - 1  # keeps the original TOTAL_SPEED/BOUNCE_SPEED=8/7 ratio
    pc = paddle.centery
    bc = ball.centery
    ri = bc - pc
    ni = ri / (PONG_PADDLE_H / 2)
    ni = max(-0.9, min(0.9, ni))
    new_ball_speed_y = ni * bounce_speed
    new_ball_speed_x = maths.sqrt(max(0, total_speed**2 - new_ball_speed_y**2))
    return new_ball_speed_x, new_ball_speed_y


# == Drawing helpers ==================================================

def draw_pong_board(surface, p1_rect, p2_rect, ball_rect,
                    p1_score, p2_score,
                    p1_colour=COL_PLAYER, p2_colour=COL_AI,
                    ball_colour=COL_WHITE,
                    font_big=None, font_body=None):
    """Draw the full pong playfield with scores."""
    if font_big is None:
        font_big = title_font()
    if font_body is None:
        font_body = body_font()

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
        self.font_title = title_font()
        self.font_body = body_font()

        # difficulty gets attached by DifficultySelectScreen/carousel_menu.py
        # BEFORE startup() runs - see _apply_difficulty() below. If nothing
        # attached one (old save path, or a mode launched without going
        # through difficulty select) these just keep the original hardcoded
        # numbers, so nothing breaks for a mode that doesn't have one yet.
        self.difficulty = None
        self._base_speed = TOTAL_SPEED
        self._current_speed = TOTAL_SPEED
        self.paddle_speed = PADDLE_MAX_SPEED  # player's own movement speed - see _apply_difficulty()

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
                total_speed=self._current_speed,
            )
            # left paddle = positive x direction
            self.ball_speed_x = abs(self.ball_speed_x)
            self._on_paddle_hit()

    def _check_paddle_hit_right(self, paddle):
        """AI/right-paddle collision. Updates ball speed in-place."""
        if self.ball.colliderect(paddle) and self.ball_speed_x >= 0:
            self.ball_speed_x, self.ball_speed_y = paddle_bounce(
                self.ball, paddle, self.ball_speed_x, self.ball_speed_y,
                total_speed=self._current_speed,
            )
            # right paddle = negative x direction
            self.ball_speed_x = -abs(self.ball_speed_x)
            self._on_paddle_hit()

    def _on_paddle_hit(self):
        """Hell-style difficulties: ball gets a bit faster every paddle
        hit. reset_ball() (called on every score, see _check_scoring)
        brings _current_speed back down to the difficulty's base speed,
        so this only ramps up within a single rally."""
        if self.difficulty and getattr(self.difficulty, "speed_up_on_hit", False):
            self._current_speed += getattr(self.difficulty, "speed_up_amount", 1)

    def _apply_difficulty(self):
        """
        Call this from a mode's startup(), after super().startup(persist),
        and before reset_ball(). Pulls ball/paddle/AI tuning out of
        whatever Difficulty object got attached to us (see
        DifficultySelectScreen and carousel_menu.py's
        _proceed_to_difficulty_or_launch). If this game/mode was launched
        without going through difficulty select, self.difficulty is just
        None and everything keeps using the original hardcoded defaults.
        """
        diff = getattr(self, "difficulty", None)
        self._base_speed = diff.ball_base_speed if diff else TOTAL_SPEED
        self.paddle_speed = diff.paddle_speed if diff else PADDLE_MAX_SPEED

        # Pong2PMode has no self.ai, so this is skipped there - the ball
        # tuning above still applies to both modes
        if diff and hasattr(self, "ai"):
            self.ai.speed = diff.ai_speed
            self.ai.predictive = diff.ai_predictive
            self.ai.error = diff.ai_error

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
        """
        Centre the ball and re-serve it at the difficulty's base speed
        (self._base_speed - just TOTAL_SPEED if no difficulty was ever
        attached). This is also where _current_speed gets put back down
        after a Hell-style rally sped it up - reset_ball() runs on every
        single score, see _check_scoring below.
        """
        self.ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self._current_speed = self._base_speed

        x_dir = -1 if self.ball_speed_x > 0 else 1
        y_dir = 1 if self.ball_speed_y >= 0 else -1

        if self.difficulty and getattr(self.difficulty, "randomise_ball", False):
            y_frac = random.uniform(0.15, 0.6)  # less predictable serve angle
        else:
            y_frac = 0.35  # same gentle angle every time (close to the original fixed "5")

        self.ball_speed_y = y_dir * self._current_speed * y_frac
        self.ball_speed_x = x_dir * maths.sqrt(max(0, self._current_speed ** 2 - self.ball_speed_y ** 2))

    # == shared submit / cleanup ==

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.pause_requested = True
        return None

    def cleanup(self):
        pass