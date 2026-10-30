GAME_NAME = 'Guess Number'

# ======[ G U E S S   N U M B E R   —   I N I T ]======
# guess the number — play against AI or local hot-seat

from src.games.guess_number.mode_ai import GuessNumAIMode
from src.games.guess_number.mode_local import GuessNumLocalMode

MODES = {
    "Vs AI":      "mode_ai",
    "Vs Local":   "mode_local",
}