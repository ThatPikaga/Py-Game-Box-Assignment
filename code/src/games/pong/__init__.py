# ======[ P O N G   —   I N I T ]======
# exports MODES dict so the carousel knows what modes this game has
# each mode is a separate .py file in this folder

from src.games.pong.mode_ai import PongAIMode
from src.games.pong.mode_2p import Pong2PMode

MODES = {
    "Vs AI":      "mode_ai",
    "2 Players":  "mode_2p",
}