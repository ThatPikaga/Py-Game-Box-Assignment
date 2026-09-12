# ======[ T E T R I S   —   2   P L A Y E R ]======
# local multiplayer Tetris (SNES Dr. Mario style)
# two boards side-by-side; if one player's stack hits the top of
# THEIR OWN board (not the window), the OTHER player wins.
# Each player has separate input and DAS timing.

import pygame
import random
from src.core.game_base import GameBase
from src.core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    TETRIS_COLS, TETRIS_ROWS, TETRIS_CELL,
    TETRIS_BOARD_W, TETRIS_BOARD_H,
    COL_BG, COL_BOARD_BG, COL_BOARD_BDR, COL_TEXT,
    COL_DARK_RED, COL_GHOST, COL_LOSE, COL_WIN,
    COL_TEXT_MUTED, COL_PLAYER, COL_DARK_GREEN,
    PC, SH, PN,
    FONT_TITLE_SIZE, FONT_BODY_SIZE,
)
from src.engine.input_handler import GameKeyHandler, GAME_KEY_MAPS
from src.games.tetris.mode_1p import Board  # reuse the Board class

# board positions
P1_OX = 50
P2_OX = SCREEN_WIDTH - 50 - TETRIS_BOARD_W
BOARD_OY = 70

class Tetris2PMode(GameBase):
    """
    Two boards, two players, one winner.
    P1: arrows + space.  P2: WASD + shift.
    First player to top-out on their own board loses.
    """

    def __init__(self):
        super().__init__()
        self.name = "Tetris 2 Players"

        self.board1 = Board()
        self.board2 = Board()

        self.p1_input = GameKeyHandler(GAME_KEY_MAPS["tetris_p1"])
        self.p2_input = GameKeyHandler(GAME_KEY_MAPS["tetris_p2"])

        # DAS constants — NES-style (same as 1P mode)
        self.DAS_DELAY = 167
        self.DAS_REPEAT = 16    # then zip across (~60 Hz)

        self.gravity_timer = 0
        self.gravity_interval = 167

        self.font_large = pygame.font.Font(None, FONT_TITLE_SIZE)
        self.font_body = pygame.font.Font(None, FONT_BODY_SIZE)

        self.state = "PLAYING"
        self.winner_msg = ""

    def startup(self, persist):
        super().startup(persist)
        self.state = "PLAYING"
        self.board1 = Board()
        self.board2 = Board()
        self.board1.sfx = self.sfx
        self.board2.sfx = self.sfx
        self.gravity_timer = 0
        self.winner_msg = ""
        self.p1_input.clear()
        self.p2_input.clear()

    def handle_event(self, event):
        # P1 input
        action = self.p1_input.handle_event(event)
        if self.state == "PLAYING" and not self.board1.game_over:
            if action == "LEFT": self.board1.move_left()
            elif action == "RIGHT": self.board1.move_right()
            elif action == "DOWN": self.board1.move_down()
            elif action == "ROTATE": self.board1.rotate()
            elif action == "DROP": self.board1.hard_drop()

        # P2 input
        action2 = self.p2_input.handle_event(event)
        if self.state == "PLAYING" and not self.board2.game_over:
            if action2 == "LEFT": self.board2.move_left()
            elif action2 == "RIGHT": self.board2.move_right()
            elif action2 == "DOWN": self.board2.move_down()
            elif action2 == "ROTATE": self.board2.rotate()
            elif action2 == "DROP": self.board2.hard_drop()

        # GAME_OVER state: E/ENTER/mouse returns to mode select
        if self.state == "GAME_OVER":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_e, pygame.K_RETURN):
                    return "MAIN_MENU"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return "MAIN_MENU"

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.pause_requested = True
        return None

    def update(self, dt):
        if self.state != "PLAYING":
            return

        self.gravity_timer += dt
        if self.gravity_timer >= self.gravity_interval:
            self.gravity_timer = 0
            if not self.board1.game_over:
                self.board1.move_down()
            if not self.board2.game_over:
                self.board2.move_down()

        # DAS for P1 — NES-style 500ms delay then rapid repeat
        active1 = self.p1_input.get_active()
        if active1 == "LEFT":
            if self.p1_input.das("LEFT", self.DAS_DELAY, self.DAS_REPEAT):
                self.board1.move_left()
        elif active1 == "RIGHT":
            if self.p1_input.das("RIGHT", self.DAS_DELAY, self.DAS_REPEAT):
                self.board1.move_right()

        # DAS for P2 — same NES-style timing
        active2 = self.p2_input.get_active()
        if active2 == "LEFT":
            if self.p2_input.das("LEFT", self.DAS_DELAY, self.DAS_REPEAT):
                self.board2.move_left()
        elif active2 == "RIGHT":
            if self.p2_input.das("RIGHT", self.DAS_DELAY, self.DAS_REPEAT):
                self.board2.move_right()

        # check for game over
        if self.board1.game_over and not self.board2.game_over:
            self.winner_msg = "Player 2 Wins!"
            self.state = "GAME_OVER"
        elif self.board2.game_over and not self.board1.game_over:
            self.winner_msg = "Player 1 Wins!"
            self.state = "GAME_OVER"
        elif self.board1.game_over and self.board2.game_over:
            self.winner_msg = "Draw!"
            self.state = "GAME_OVER"

    def draw(self, surface):
        surface.fill(COL_BG)

        # draw both boards
        self._draw_board(surface, self.board1, P1_OX, BOARD_OY, "P1")
        self._draw_board(surface, self.board2, P2_OX, BOARD_OY, "P2")

        # hint between boards
        hint = self.font_body.render("First to top loses!", True, COL_TEXT_MUTED)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 20))

        # game over overlay
        if self.state == "GAME_OVER":
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 180))
            surface.blit(ov, (0, 0))
            wl = self.font_large.render(self.winner_msg, True, COL_DARK_GREEN)
            surface.blit(wl, (SCREEN_WIDTH // 2 - wl.get_width() // 2, 400))
            sub = self.font_body.render("Press E or ENTER to return", True, COL_TEXT)
            surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 480))

    def _draw_board(self, surface, board, ox, oy, label):
        pygame.draw.rect(surface, COL_BOARD_BG, (ox, oy, TETRIS_BOARD_W, TETRIS_BOARD_H))
        pygame.draw.rect(surface, COL_BOARD_BDR, (ox, oy, TETRIS_BOARD_W, TETRIS_BOARD_H), 2)

        for r in range(TETRIS_ROWS):
            for c in range(TETRIS_COLS):
                clr = board.get_grid_cell(r, c)
                if clr:
                    pygame.draw.rect(surface, PC.get(clr, COL_DARK_GREEN),
                                     (ox + c * TETRIS_CELL + 1, oy + r * TETRIS_CELL + 1,
                                      TETRIS_CELL - 2, TETRIS_CELL - 2))

        if board.current and not board.game_over:
            n, s, px, py, rot = board.current
            srot = board._rotated(s, rot)
            gy = board._ghost_y()
            for ri, row in enumerate(srot):
                for ci, v in enumerate(row):
                    if v:
                        pygame.draw.rect(surface, COL_GHOST,
                                         (ox + (px + ci) * TETRIS_CELL + 1,
                                          oy + (gy + ri) * TETRIS_CELL + 1,
                                          TETRIS_CELL - 2, TETRIS_CELL - 2), 1)
                        pygame.draw.rect(surface, PC.get(n, COL_DARK_GREEN),
                                         (ox + (px + ci) * TETRIS_CELL + 1,
                                          oy + (py + ri) * TETRIS_CELL + 1,
                                          TETRIS_CELL - 2, TETRIS_CELL - 2))

        lbl = self.font_body.render(f"{label}: {board.score}", True, COL_WIN if label == "P1" else COL_DARK_GREEN)
        surface.blit(lbl, (ox, oy - 30))

        if board.game_over:
            ov = pygame.Surface((TETRIS_BOARD_W, TETRIS_BOARD_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 140))
            surface.blit(ov, (ox, oy))

    def cleanup(self):
        self.p1_input.clear()
        self.p2_input.clear()