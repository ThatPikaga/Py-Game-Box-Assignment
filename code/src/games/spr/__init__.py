GAME_NAME = 'Scissors Paper Rock'

# ======[ S P R   —   I N I T ]======
# scissors paper rock — local 2P or vs AI

from src.games.spr.mode_ai import SPRAIMode
from src.games.spr.mode_2p import SPR2PMode

MODES = {
    "Vs AI":      "mode_ai",
    "2 Players":  "mode_2p",
}