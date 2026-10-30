GAME_NAME = 'Tetris'

# ======[ T E T R I S   —   I N I T ]======
# Tetris has two modes: single player and local 2P (SNES style)

from src.games.tetris.mode_1p import Tetris1PMode
from src.games.tetris.mode_2p import Tetris2PMode

MODES = {
    "1 Player":  "mode_1p",
    "2 Players": "mode_2p",
}