GAME_NAME = 'Memory Match'

# ======[ M E M O R Y   —   I N I T ]======
# memory match game — local single, 2P, or vs AI

from src.games.memory.mode_1p import Memory1PMode
from src.games.memory.mode_2p import Memory2PMode
from src.games.memory.mode_ai import MemoryAIMode

MODES = {
    "Single Player":   "mode_1p",
    "Local Vs":  "mode_2p",
    "Vs AI":      "mode_ai",
}