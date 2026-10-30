# single player pong against the AI

import pygame
import math as maths
from src.core.game_base import GameBase
from src.core.constants import *
from src.engine.input_handler import GameKeyHandler
from src.games.pong.ai import AI
from src.games.pong.common import (
    PongBaseMode, make_paddle_rect, make_paddle_rect_right,
    make_ball_rect, draw_pong_board,
    PONG_WIN_SCORE, PONG_PLAY_AGAIN_RECT, draw_pong_game_over,
)

class PongAIMode(PongBaseMode):
    def __init__(self):
        super().__init__()
        self.name = "Pong Vs AI"
        self.state = "PLAYING"

        # === objects ===
        self.player = make_paddle_rect(50)
        self.opponent = make_paddle_rect_right()
        self.ball = make_ball_rect()

        self.ball_speed_x = 5
        self.ball_speed_y = 5

        # uses the new input handler so held-key tracking works
        self.input = GameKeyHandler({
            "P1_UP":   pygame.K_w,
            "P1_DOWN": pygame.K_s,
        })

        # AI
        self.ai = AI(speed=7)

        # scores
        self.player_score = 0
        self.opponent_score = 0

    def startup(self, persist):
        super().startup(persist)
        self._apply_difficulty()  # pulls ball speed + AI tuning off self.difficulty, if any
        self.state = "PLAYING"
        self.player_score = 0
        self.opponent_score = 0
        self.winner_msg = ""
        self.reset_ball()
        self.input.clear()

    def handle_event(self, event):
        self.input.handle_event(event)  # let the handler track key state
        if self.state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_e):
                return "PLAY_AGAIN"
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                    and PONG_PLAY_AGAIN_RECT.collidepoint(event.pos)):
                return "PLAY_AGAIN"
        return super().handle_event(event)

    def update(self, dt):
        if self.state != "PLAYING":
            return

        # === player movement (fixed: uses most-recent held key) ===
        active = self.input.get_active()
        if active == "P1_UP":
            self.player.y -= self.paddle_speed
        elif active == "P1_DOWN":
            self.player.y += self.paddle_speed

        self.player.top = max(0, self.player.top)
        self.player.bottom = min(SCREEN_HEIGHT, self.player.bottom)

        # AI movement (extra args only matter if this difficulty's AI is
        # predictive - AI.move() just ignores them for the Basic AI)
        self.ai.move(self.opponent, self.ball, self.ball_speed_x, self.ball_speed_y, SCREEN_HEIGHT)
        self.opponent.top = max(0, self.opponent.top)
        self.opponent.bottom = min(SCREEN_HEIGHT, self.opponent.bottom)

        # ball movement
        self._update_ball()

        # player paddle hit
        self._check_paddle_hit_left(self.player)

        # opponent paddle hit
        self._check_paddle_hit_right(self.opponent)

        # scoring
        self._check_scoring()

    def _on_left_scored(self):
        """Player scored."""
        self.player_score += 1
        if self.player_score >= PONG_WIN_SCORE:
            self.winner_msg = "You Win!"
            self.state = "GAME_OVER"

    def _on_right_scored(self):
        """Opponent (AI) scored."""
        self.opponent_score += 1
        if self.opponent_score >= PONG_WIN_SCORE:
            self.winner_msg = "AI Wins!"
            self.state = "GAME_OVER"

    def draw(self, surface):
        draw_pong_board(
            surface,
            self.player, self.opponent, self.ball,
            self.player_score, self.opponent_score,
            p1_colour=COL_WHITE, p2_colour=COL_WHITE,
            font_big=self.font_title, font_body=self.font_body,
        )
        if self.state == "GAME_OVER":
            draw_pong_game_over(surface, self.winner_msg)

    def cleanup(self):
        self.input.clear()