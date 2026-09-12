# ======[ P O N G   —   2   P L A Y E R ]======
# local 2-player pong on the same keyboard
# P1 uses W/S, P2 uses UP/DOWN

import pygame
import math as maths
from src.core.game_base import GameBase
from src.core.constants import *
from src.engine.input_handler import GameKeyHandler
from src.games.pong.common import (
    PongBaseMode, make_paddle_rect, make_paddle_rect_right,
    make_ball_rect, draw_pong_board,
)

class Pong2PMode(PongBaseMode):
    def __init__(self):
        super().__init__()
        self.name = "Pong 2 Players"

        # ── objects —─
        self.p1 = make_paddle_rect(50)
        self.p2 = make_paddle_rect_right()
        self.ball = make_ball_rect()

        self.ball_speed_x = 5
        self.ball_speed_y = 5

        # separate input handlers for each player
        self.p1_input = GameKeyHandler({
            "P1_UP":   pygame.K_w,
            "P1_DOWN": pygame.K_s,
        })
        self.p2_input = GameKeyHandler({
            "P2_UP":   pygame.K_UP,
            "P2_DOWN": pygame.K_DOWN,
        })

        self.p1_score = 0
        self.p2_score = 0

    def startup(self, persist):
        super().startup(persist)
        self.p1_score = 0
        self.p2_score = 0
        self.reset_ball()
        self.p1_input.clear()
        self.p2_input.clear()

    def handle_event(self, event):
        self.p1_input.handle_event(event)
        self.p2_input.handle_event(event)
        return super().handle_event(event)

    def update(self, dt):
        # P1 movement
        a1 = self.p1_input.get_active()
        if a1 == "P1_UP":
            self.p1.y -= TOTAL_SPEED
        elif a1 == "P1_DOWN":
            self.p1.y += TOTAL_SPEED
        self.p1.top = max(0, self.p1.top)
        self.p1.bottom = min(SCREEN_HEIGHT, self.p1.bottom)

        # P2 movement
        a2 = self.p2_input.get_active()
        if a2 == "P2_UP":
            self.p2.y -= TOTAL_SPEED
        elif a2 == "P2_DOWN":
            self.p2.y += TOTAL_SPEED
        self.p2.top = max(0, self.p2.top)
        self.p2.bottom = min(SCREEN_HEIGHT, self.p2.bottom)

        # ball
        self._update_ball()

        # P1 paddle hit
        self._check_paddle_hit_left(self.p1)

        # P2 paddle hit
        self._check_paddle_hit_right(self.p2)

        # scoring
        self._check_scoring()

    def _on_left_scored(self):
        """P2 scored (ball went past P1's left edge)."""
        self.p2_score += 1

    def _on_right_scored(self):
        """P1 scored (ball went past P2's right edge)."""
        self.p1_score += 1

    def draw(self, surface):
        draw_pong_board(
            surface,
            self.p1, self.p2, self.ball,
            self.p1_score, self.p2_score,
            p1_colour=COL_PLAYER, p2_colour=COL_AI,
            font_big=self.font_big, font_body=self.font_body,
        )

        # labels
        p1l = self.font_body.render("P1 (W/S)", True, COL_TEXT_MUTED)
        p2l = self.font_body.render("P2 (Up/Down)", True, COL_TEXT_MUTED)
        surface.blit(p1l, (SCREEN_WIDTH // 4 - p1l.get_width() // 2, 60))
        surface.blit(p2l, (3 * SCREEN_WIDTH // 4 - p2l.get_width() // 2, 60))

    def cleanup(self):
        self.p1_input.clear()
        self.p2_input.clear()