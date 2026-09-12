# ======[ T E T R I S   —   1   P L A Y E R ]======
# standard single-player Tetris with a next-piece preview and ghost piece
# uses the new GameBase so the state machine treats it like everything else
#
# Key things:
# - DAS for left/right: hold 500ms then rapid repeat (NES-style, feels
#   like the original Tetris on the NES — you hold a direction, there's
#   a deliberate pause, then it zooms across)
# - gravity speeds up as you clear lines (every 10 lines)
# - ghost piece shows where the current piece would land
# - ESC → pause_requested (handled by the wrapper), game over → back to mode select

import pygame
import random
from src.core.game_base import GameBase
from src.core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    TETRIS_COLS, TETRIS_ROWS, TETRIS_CELL,
    TETRIS_BOARD_W, TETRIS_BOARD_H,
    COL_BG, COL_BOARD_BG, COL_BOARD_BDR, COL_TEXT,
    COL_DARK_GREEN, COL_DARK_RED, COL_GHOST, COL_LOSE, COL_WIN,
    PC, SH, PN,
    FONT_TITLE_SIZE, FONT_BODY_SIZE,
)
from src.engine.input_handler import GameKeyHandler


# ======[ B O A R D ]======
# the grid, current piece, next piece, line clearing, collision detection
# kept separate so 2P mode can reuse it without copy/pasting everything

class Board:
    """A single tetris board — grid, piece logic, line clearing, the works."""

    def __init__(self):
        self.grid = [[None] * TETRIS_COLS for _ in range(TETRIS_ROWS)]
        self.current = None   # [name, shape, px, py, rotation]
        self.next_piece = None
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.sfx = {}          # set by the game mode, used for sound effects

        self._generate_next()
        self._spawn_piece()

    # ===== piece helpers =====

    def _random_piece(self):
        """Pick a random piece name + shape from the constants."""
        name = random.choice(PN)
        return name, SH[name]

    def _spawn_piece(self):
        """Take the 'next' piece and make it the 'current' piece."""
        if self.next_piece is None:
            self._generate_next()
        name, shape = self.next_piece
        self.next_piece = None
        # centre horizontally, start at the top
        px = (TETRIS_COLS - len(shape[0])) // 2
        py = 0
        self.current = [name, shape, px, py, 0]

        # if it collides right away, the board is full — game over
        if self._collides(shape, px, py):
            self.game_over = True
            if self.sfx.get("life_lost"):
                try:
                    self.sfx["life_lost"].play()
                except Exception:
                    pass

    def _generate_next(self):
        """Re-roll the 'next' piece."""
        self.next_piece = self._random_piece()

    # ===== rotation & collision =====

    @staticmethod
    def _rotated(shape, times):
        """Rotate a shape 90° CW `times` times. Pure function, returns new list."""
        s = shape
        for _ in range(times % 4):
            s = [list(r) for r in zip(*s[::-1])]
        return s

    def _collides(self, shape, px, py):
        """Does this shape at (px, py) overlap the grid or go out of bounds?"""
        for ri, row in enumerate(shape):
            for ci, cell in enumerate(row):
                if cell:
                    bx = px + ci
                    by = py + ri
                    if bx < 0 or bx >= TETRIS_COLS or by >= TETRIS_ROWS:
                        return True
                    if by >= 0 and self.grid[by][bx] is not None:
                        return True
        return False

    # ===== locking & line clearing =====

    def _lock(self):
        """Bake the current piece into the grid and clear any full lines."""
        name, shape, px, py, rot = self.current
        shape = self._rotated(shape, rot)

        for ri, row in enumerate(shape):
            for ci, cell in enumerate(row):
                if cell:
                    bx = px + ci
                    by = py + ri
                    if 0 <= by < TETRIS_ROWS and 0 <= bx < TETRIS_COLS:
                        self.grid[by][bx] = name

        # clear full lines from bottom up
        cleared = 0
        for r in range(TETRIS_ROWS - 1, -1, -1):
            if all(c is not None for c in self.grid[r]):
                del self.grid[r]
                self.grid.insert(0, [None] * TETRIS_COLS)
                cleared += 1

        if cleared:
            self.lines_cleared += cleared
            # classic Tetris scoring: 1 line=100, 2=300, 3=500, 4=800
            self.score += {1: 100, 2: 300, 3: 500, 4: 800}.get(cleared, 0)
            if self.sfx.get("num_correct"):
                try:
                    self.sfx["num_correct"].play()
                except Exception:
                    pass

        self._spawn_piece()

    def _ghost_y(self):
        """Where would the current piece land if hard-dropped?"""
        name, shape, px, py, rot = self.current
        shape = self._rotated(shape, rot)
        gy = py
        while not self._collides(shape, px, gy + 1):
            gy += 1
        return gy

    # ===== movement API =====

    def move_left(self):
        if self.current and not self.game_over:
            _, shape, x, y, rot = self.current
            if not self._collides(self._rotated(shape, rot), x - 1, y):
                self.current[2] = x - 1

    def move_right(self):
        if self.current and not self.game_over:
            _, shape, x, y, rot = self.current
            if not self._collides(self._rotated(shape, rot), x + 1, y):
                self.current[2] = x + 1

    def move_down(self):
        """Soft drop one cell. Locks the piece if it can't go further."""
        if self.current and not self.game_over:
            _, shape, x, y, rot = self.current
            if not self._collides(self._rotated(shape, rot), x, y + 1):
                self.current[3] = y + 1
            else:
                self._lock()

    def hard_drop(self):
        """Drop straight to the ghost position and lock immediately."""
        if self.current and not self.game_over:
            self.current[3] = self._ghost_y()
            self._lock()

    def rotate(self):
        """Try to rotate the current piece, with wall-kicks left/right."""
        if self.current and not self.game_over:
            _, shape, x, y, rot = self.current
            new_shape = self._rotated(shape, rot + 1)
            # try offsets: 0, -1, +1, -2, +2 (simple wall kick)
            for dx in [0, -1, 1, -2, 2]:
                if not self._collides(new_shape, x + dx, y):
                    self.current[2] = x + dx
                    self.current[4] = (rot + 1) % 4
                    return

    def get_grid_cell(self, r, c):
        """Public accessor for a locked cell at (r, c) or None."""
        return self.grid[r][c]


# ======[ M O D E   C L A S S ]======
# the actual game mode that GameBase + the state machine interact with

class Tetris1PMode(GameBase):
    """Single-player Tetris with ghost piece, next preview, and DAS."""

    def __init__(self):
        super().__init__()
        self.name = "Tetris 1 Player"
        self.state = "PLAYING"

        self.board = Board()

        # input — uses the GameKeyHandler with the tetris_p1 map from constants
        # LEFT, RIGHT, DOWN, ROTATE, DROP all come from GAME_KEY_MAPS["tetris_p1"]
        self.input = GameKeyHandler({
            "LEFT":   pygame.K_LEFT,
            "RIGHT":  pygame.K_RIGHT,
            "DOWN":   pygame.K_DOWN,
            "ROTATE": pygame.K_UP,
            "DROP":   pygame.K_SPACE,
        })

        # DAS constants — NES-style: hold for half a second then rapid repeat.
        # 167ms delay feels deliberate and old-school, 16ms repeat (≈60 Hz)
        # makes the piece zip across once it's charged up.
        self.DAS_DELAY = 167    # ms before auto-repeat kicks in (default according to https://tetris.wiki/Tetris_Guideline)
        self.DAS_REPEAT = 16    # ms between repeats (~60 Hz tick)

        # gravity starts at 167ms and speeds up as lines are cleared
        self.gravity_interval = 167
        self.gravity_timer = 0

        # fonts
        self.font_large = pygame.font.Font(None, FONT_TITLE_SIZE)
        self.font_body = pygame.font.Font(None, FONT_BODY_SIZE)

    def startup(self, persist):
        """Reset everything — called by the state machine on enter."""
        super().startup(persist)
        self.state = "PLAYING"

        # fresh board, fresh everything
        self.board = Board()
        self.board.sfx = self.sfx

        self.gravity_interval = 167
        self.gravity_timer = 0
        self.input.clear()

    def handle_event(self, event):
        """Handle one input event. ESC sets pause_requested."""
        action = self.input.handle_event(event)

        if self.state == "GAME_OVER":
            # E or ENTER or mouse click → back to mode select
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_e, pygame.K_RETURN):
                    return "MAIN_MENU"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return "MAIN_MENU"

        # ESC is handled generically by GameBase.handle_event, but we
        # also call it here since we override handle_event
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
            # if after gravity the board is now game over, bail
            if self.board.game_over:
                self.state = "GAME_OVER"
                return

        # gravity speeds up as you get better — every 10 lines cleared,
        # the interval drops.  floor at 100ms so it doesn't become unplayable.
        level = self.board.lines_cleared // 10
        self.gravity_interval = max(100, 500 - level * 40)

        # ===== DAS (left / right repeat) =====
        # only repeat the most-recently-held direction, not both simultaneously
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
        oy = 70

        # ===== draw board background & border =====
        pygame.draw.rect(surface, COL_BOARD_BG, (ox, oy, TETRIS_BOARD_W, TETRIS_BOARD_H))
        pygame.draw.rect(surface, COL_BOARD_BDR, (ox, oy, TETRIS_BOARD_W, TETRIS_BOARD_H), 2)

        # ===== draw locked cells =====
        for r in range(TETRIS_ROWS):
            for c in range(TETRIS_COLS):
                clr = self.board.get_grid_cell(r, c)
                if clr:
                    colour = PC.get(clr, COL_DARK_GREEN)
                    rect = (ox + c * TETRIS_CELL + 1, oy + r * TETRIS_CELL + 1,
                            TETRIS_CELL - 2, TETRIS_CELL - 2)
                    pygame.draw.rect(surface, colour, rect)

        # ===== draw ghost piece + current piece =====
        if self.board.current and not self.board.game_over:
            name, shape, px, py, rot = self.board.current
            rotated = Board._rotated(shape, rot)
            ghost_y = self.board._ghost_y()

            for ri, row in enumerate(rotated):
                for ci, cell in enumerate(row):
                    if cell:
                        gx = ox + (px + ci) * TETRIS_CELL + 1
                        # ghost outline
                        gy = oy + (ghost_y + ri) * TETRIS_CELL + 1
                        pygame.draw.rect(
                            surface, COL_GHOST,
                            (gx, gy, TETRIS_CELL - 2, TETRIS_CELL - 2), 1
                        )
                        # actual piece
                        cy = oy + (py + ri) * TETRIS_CELL + 1
                        colour = PC.get(name, COL_DARK_GREEN)
                        pygame.draw.rect(
                            surface, colour,
                            (gx, cy, TETRIS_CELL - 2, TETRIS_CELL - 2)
                        )

        # ===== score =====
        score_text = self.font_large.render(f"Score: {self.board.score}", True, COL_TEXT)
        surface.blit(score_text, (ox, oy - 45))

        lines_text = self.font_body.render(f"Lines: {self.board.lines_cleared}", True, COL_TEXT)
        surface.blit(lines_text, (ox, oy - 20))

        # ===== next piece preview =====
        if self.board.next_piece:
            nx = ox + TETRIS_BOARD_W + 20
            ny = oy + 40
            label = self.font_body.render("Next:", True, COL_TEXT)
            surface.blit(label, (nx, ny - 30))

            nn, ns = self.board.next_piece
            preview_cell = 20  # smaller cells for the preview
            for ri, row in enumerate(ns):
                for ci, cell in enumerate(row):
                    if cell:
                        colour = PC.get(nn, COL_DARK_GREEN)
                        pygame.draw.rect(
                            surface, colour,
                            (nx + ci * preview_cell, ny + ri * preview_cell,
                             preview_cell - 2, preview_cell - 2)
                        )

        # ===== GAME OVER overlay =====
        if self.state == "GAME_OVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))

            go_text = self.font_large.render("GAME OVER", True, COL_LOSE)
            surface.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2,
                                   SCREEN_HEIGHT // 2 - 60))

            score_final = self.font_body.render(f"Final Score: {self.board.score}", True, COL_TEXT)
            surface.blit(score_final, (SCREEN_WIDTH // 2 - score_final.get_width() // 2,
                                       SCREEN_HEIGHT // 2))

            sub_text = self.font_body.render("Press E or ENTER to return", True, COL_TEXT)
            surface.blit(sub_text, (SCREEN_WIDTH // 2 - sub_text.get_width() // 2,
                                    SCREEN_HEIGHT // 2 + 40))

    def cleanup(self):
        """Clean up input state when switching away."""
        self.input.clear()