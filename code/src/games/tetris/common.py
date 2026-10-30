# ======[ T E T R I S   —   C O M M O N ]======
import pygame
import random
from src.core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, scale_size,
    TETRIS_COLS, TETRIS_ROWS, TETRIS_CELL,
    TETRIS_BOARD_W, TETRIS_BOARD_H,
    COL_BG, COL_BOARD_BG, COL_BOARD_BDR, COL_TEXT, COL_TEXT_MUTED,
    COL_DARK_GREEN, COL_GHOST, COL_LOSE, COL_WIN, COL_DARK_RED,
    PC, SH, PN,
)

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
        return cleared

    def add_garbage_rows(self, count):
        """Push the stack up and add one partly-filled row for each line scored."""
        for _ in range(count):
            if any(cell is not None for cell in self.grid[0]):
                self.game_over = True
            self.grid.pop(0)
            row = ["G"] * TETRIS_COLS
            row[random.randrange(TETRIS_COLS)] = None
            self.grid.append(row)

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
        """Soft drop one cell. Returns cleared rows if the piece locks."""
        if self.current and not self.game_over:
            _, shape, x, y, rot = self.current
            if not self._collides(self._rotated(shape, rot), x, y + 1):
                self.current[3] = y + 1
            else:
                return self._lock()
        return 0

    def hard_drop(self):
        """Drop straight to the ghost position and return how many rows cleared."""
        if self.current and not self.game_over:
            self.current[3] = self._ghost_y()
            return self._lock()
        return 0

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


# ======[ D R A W I N G   H E L P E R S ]======

def draw_board_grid_and_pieces(surface, board, ox, oy):
    """Draws the board background, locked cells, current piece, ghost piece, and game-over dimming."""
    pygame.draw.rect(surface, COL_BOARD_BG, (ox, oy, TETRIS_BOARD_W, TETRIS_BOARD_H))
    pygame.draw.rect(surface, COL_BOARD_BDR, (ox, oy, TETRIS_BOARD_W, TETRIS_BOARD_H), scale_size(2))

    # locked cells
    for r in range(TETRIS_ROWS):
        for c in range(TETRIS_COLS):
            clr = board.get_grid_cell(r, c)
            if clr:
                pygame.draw.rect(surface, PC.get(clr, COL_DARK_GREEN),
                                 (ox + c * TETRIS_CELL + scale_size(1), oy + r * TETRIS_CELL + scale_size(1),
                                  TETRIS_CELL - scale_size(2), TETRIS_CELL - scale_size(2)))

    # current + ghost piece
    if board.current and not board.game_over:
        n, s, px, py, rot = board.current
        srot = Board._rotated(s, rot)
        gy = board._ghost_y()
        for ri, row in enumerate(srot):
            for ci, v in enumerate(row):
                if v:
                    # ghost outline
                    pygame.draw.rect(surface, COL_GHOST,
                                     (ox + (px + ci) * TETRIS_CELL + scale_size(1),
                                      oy + (gy + ri) * TETRIS_CELL + scale_size(1),
                                      TETRIS_CELL - scale_size(2), TETRIS_CELL - scale_size(2)), scale_size(1))
                    # actual piece
                    pygame.draw.rect(surface, PC.get(n, COL_DARK_GREEN),
                                     (ox + (px + ci) * TETRIS_CELL + scale_size(1),
                                      oy + (py + ri) * TETRIS_CELL + scale_size(1),
                                      TETRIS_CELL - scale_size(2), TETRIS_CELL - scale_size(2)))

    # dim board if game over
    if board.game_over:
        ov = pygame.Surface((TETRIS_BOARD_W, TETRIS_BOARD_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 140))
        surface.blit(ov, (ox, oy))