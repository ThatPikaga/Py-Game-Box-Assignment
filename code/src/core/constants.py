# ======[ S H A R E D   C O N S T A N T S ]======
# one file to rule them all - colours, sizes, fonts
# every game imports from here so I don't have to retype the same rgb
# triplets eighteen times across six files like a madman

import pygame

# == Window / Screen ================================================
# these get referenced by settings.py too but this is the source of truth
SCREEN_WIDTH = 950
SCREEN_HEIGHT = 950

# == COLOURS! ============================================
COL_BG          = (5, 5, 15)
COL_CARD_BG     = (25, 25, 50)
COL_CARD_BORDER = (80, 80, 140)
COL_TEXT        = (230, 230, 250) # primary text
COL_TEXT_MUTED  = (150, 150, 180) # secondary/hints
COL_PLAYER      = (16, 185, 129) # green - player 1
COL_AI          = (239, 68, 68) # red - ai / player 2
COL_WIN         = (0, 255, 0)
COL_LOSE        = (255, 50, 50)
COL_GHOST       = (40, 40, 80) # tetris ghost piece
COL_BOARD_BG    = (15, 15, 35) # game board background
COL_BOARD_BDR   = (60, 60, 120)# game board border

# More colours
COL_WHITE       = (255, 255, 255)
COL_BLACK       = (0, 0, 0)
COL_YELLOW      = (255, 187, 0)
COL_BLUE        = (20, 110, 255)
COL_CYAN        = (0, 180, 255)
COL_ORANGE      = (255, 165, 0)
COL_PURPLE      = (128, 0, 128)
COL_PINK        = (255, 192, 203)
COL_LIME        = (50, 205, 50)
COL_TEAL        = (0, 128, 128)
COL_MAGENTA     = (255, 0, 255)
COL_GOLD        = (255, 215, 0)
COL_SILVER      = (192, 192, 192)
COL_DARK_RED    = (139, 0, 0)
COL_DARK_GREEN  = (0, 100, 0)
COL_DARK_BLUE   = (0, 0, 139)
COL_LIGHT_GRAY  = (211, 211, 211)
COL_DARK_GRAY   = (169, 169, 169)
COL_NAVY        = (0, 0, 128)
COL_MAROON      = (128, 0, 0)
COL_OLIVE       = (128, 128, 0)
COL_AQUA        = (127, 255, 212)
COL_GREEN       = (45, 207, 0)


# == Paddle / Ball defaults (Pong & Breakout) ========================================
PADDLE_W = 120
PADDLE_H = 15
PONG_PADDLE_W = 15
PONG_PADDLE_H = 120
BALL_SIZE = 15
PADDLE_MAX_SPEED = 8
TOTAL_SPEED = 8
BOUNCE_SPEED = TOTAL_SPEED - 1


# == Brick Layout for Breakout==================================================
ROWS = 6
COLS = 15
PADDING = 3
OFFSET_TOP = 60

# == Tetris ========================================================
TETRIS_COLS, TETRIS_ROWS, TETRIS_CELL = 10, 20, 28
TETRIS_BOARD_W = TETRIS_COLS * TETRIS_CELL
TETRIS_BOARD_H = TETRIS_ROWS * TETRIS_CELL

# Tetris piece colours (rgb)
PC = {
    "I": (0, 240, 240), "O": (240, 240, 0), "T": (160, 0, 240),
    "S": (0, 240, 0),   "Z": (240, 0, 0),   "J": (0, 0, 240),
    "L": (240, 160, 0),
}

# Tetris piece shapes
SH = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]],
    "L": [[0, 0, 1], [1, 1, 1]],
}
PN = list(SH.keys())

# == Memory Card ====================================================
MEMORY_CARD_W = 55
MEMORY_CARD_H = 75



# == Font sizes (None = pygame default font) ========================
FONT_TITLE_SIZE = 42
FONT_HEADER_SIZE = 28
FONT_BODY_SIZE = 20

# Helper: quick font grab so I don't pygame.font.Font() everywhere
def make_font(size, bold=False, name=None):
    """Return a font. Name=None uses pygame default (good enough)."""
    return pygame.font.Font(name, size)

def title_font():
    return make_font(FONT_TITLE_SIZE)

def header_font():
    return make_font(FONT_HEADER_SIZE)

def body_font():
    return make_font(FONT_BODY_SIZE)