# ======[ T E T R I S   —   1   P L A Y E R ]======
# standard single-player Tetris with a next-piece preview and ghost piece

import pygame
import random
from src.core.game_base import GameBase
from src.core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, scale_x, scale_y, scale_size,
    TETRIS_COLS, TETRIS_ROWS, TETRIS_CELL,
    TETRIS_BOARD_W, TETRIS_BOARD_H,
    COL_BG, COL_BOARD_BG, COL_BOARD_BDR, COL_TEXT,
    COL_DARK_GREEN, COL_DARK_RED, COL_GHOST, COL_LOSE, COL_WIN,
    PC, SH, PN,
    title_font, body_font,
)
from src.engine.input_handler import GameKeyHandler
from src.games.tetris.common import Board, draw_board_grid_and_pieces

# ======[ M O D E   C L A S S ]======

class Tetris1PMode(GameBase):
    """Single-player Tetris with ghost piece, next preview, and DAS."""

    def __init__(self):
        super().__init__()
        self.name = "Tetris 1 Player"
        self.state = "PLAYING"
        self.difficulty = None
        self.gravity_base_interval = 500

        self.board = Board()

        # input — uses the GameKeyHandler
        self.input = GameKeyHandler({
            "LEFT":   pygame.K_LEFT,
            "RIGHT":  pygame.K_RIGHT,
            "DOWN":   pygame.K_DOWN,
            "ROTATE": pygame.K_UP,
            "DROP":   pygame.K_SPACE,
        })

        # DAS constants — NES-style: hold for half a second then rapid repeat.
        self.DAS_DELAY = 167    # ms before auto-repeat kicks in
        self.DAS_REPEAT = 16    # ms between repeats (~60 Hz tick)

        # gravity starts at 167ms and speeds up as lines are cleared
        self.gravity_interval = 167
        self.gravity_timer = 0

        # Custom fonts from constants.py
        self.font_large = title_font()
        self.font_body = body_font()
        self.play_again_btn = pygame.Rect(
            SCREEN_WIDTH // 2 - scale_x(110),
            SCREEN_HEIGHT // 2 + scale_y(80),
            scale_x(220), scale_y(48),
        )

    def startup(self, persist):
        """Reset everything — called by the state machine on enter."""
        super().startup(persist)
        self.state = "PLAYING"

        # fresh board, fresh everything
        self.board = Board()
        self.board.sfx = self.sfx

        self.gravity_base_interval = getattr(self.difficulty, "gravity_interval", 500)
        self.gravity_interval = self.gravity_base_interval
        self.gravity_timer = 0
        self.input.clear()

    def handle_event(self, event):
        """Handle one input event. ESC sets pause_requested."""
        action = self.input.handle_event(event)

        if self.state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_e, pygame.K_RETURN):
                return "PLAY_AGAIN"
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                    and self.play_again_btn.collidepoint(event.pos)):
                return "PLAY_AGAIN"

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.pause_requested = True

        if self.state != "PLAYING" or self.board.game_over:
            return None

        # one-shot actions (not repeated by DAS)
        if action == "DROP":
            self.board.hard_drop()
        elif action == "ROTATE":
            self.board.rotate()
        elif action == "DOWN":
            self.board.move_down()

        return None

    def update(self, dt):
        """Update per-frame: gravity timer, DAS repeat, game-over check."""
        if self.state != "PLAYING":
            return

        # ===== check game over =====
        if self.board.game_over:
            self.state = "GAME_OVER"
            return

        # ===== gravity =====
        self.gravity_timer += dt
        if self.gravity_timer >= self.gravity_interval:
            self.gravity_timer = 0
            self.board.move_down()
            if self.board.game_over:
                self.state = "GAME_OVER"
                return

        # gravity speeds up as you get better
        level = self.board.lines_cleared // 10
        self.gravity_interval = max(80, self.gravity_base_interval - level * 40)

        # ===== DAS (left / right repeat) =====
        active = self.input.get_active()
        if active == "LEFT":
            if self.input.das("LEFT", self.DAS_DELAY, self.DAS_REPEAT):
                self.board.move_left()
        elif active == "RIGHT":
            if self.input.das("RIGHT", self.DAS_DELAY, self.DAS_REPEAT):
                self.board.move_right()

    def draw(self, surface):
        """Draw the board, ghost piece, next preview, and HUD."""
        surface.fill(COL_BG)

        ox = (SCREEN_WIDTH - TETRIS_BOARD_W) // 2
        oy = scale_y(70)

        # Draw board grid, pieces, and game-over dimming using common helper
        draw_board_grid_and_pieces(surface, self.board, ox, oy)

        # ===== HUD =====
        score_text = self.font_large.render(f"Score: {self.board.score}", True, COL_TEXT)
        surface.blit(score_text, (ox, oy - scale_y(45)))

        lines_text = self.font_body.render(f"Lines: {self.board.lines_cleared}", True, COL_TEXT)
        surface.blit(lines_text, (ox, oy - scale_y(20)))

        # ===== next piece preview =====
        if self.board.next_piece:
            nx = ox + TETRIS_BOARD_W + scale_x(20)
            ny = oy + scale_y(40)
            label = self.font_body.render("Next:", True, COL_TEXT)
            surface.blit(label, (nx, ny - scale_y(30)))

            nn, ns = self.board.next_piece
            preview_cell = scale_size(20)  # smaller cells for the preview
            for ri, row in enumerate(ns):
                for ci, cell in enumerate(row):
                    if cell:
                        colour = PC.get(nn, COL_DARK_GREEN)
                        pygame.draw.rect(
                            surface, colour,
                            (nx + ci * preview_cell, ny + ri * preview_cell,
                             preview_cell - scale_size(2), preview_cell - scale_size(2))
                        )

        # ===== GAME OVER overlay =====
        if self.state == "GAME_OVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))

            go_text = self.font_large.render("GAME OVER", True, COL_LOSE)
            surface.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2,
                                   SCREEN_HEIGHT // 2 - scale_y(60)))

            score_final = self.font_body.render(f"Final Score: {self.board.score}", True, COL_TEXT)
            surface.blit(score_final, (SCREEN_WIDTH // 2 - score_final.get_width() // 2,
                                       SCREEN_HEIGHT // 2))

            sub_text = self.font_body.render("Press E / ENTER or select Play Again", True, COL_TEXT)
            surface.blit(sub_text, (SCREEN_WIDTH // 2 - sub_text.get_width() // 2,
                                    SCREEN_HEIGHT // 2 + scale_y(35)))
            pygame.draw.rect(surface, COL_DARK_RED, self.play_again_btn, border_radius=7)
            pygame.draw.rect(surface, COL_WIN, self.play_again_btn, 2, border_radius=7)
            button = self.font_body.render("PLAY AGAIN", True, COL_TEXT)
            surface.blit(button, button.get_rect(center=self.play_again_btn.center))

    def cleanup(self):
        """Clean up input state when switching away."""
        self.input.clear()