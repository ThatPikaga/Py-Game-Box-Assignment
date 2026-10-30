# Medium - 26 pairs on the board (52 cards).
# Bigger board AND a better memory. The AI can keep track of the last
# 5 cards it has seen, so it'll start picking up pairs more often.

from src.games.memory.difficulties._base import MemoryDifficulty

class Difficulty(MemoryDifficulty):
    name = "Medium"
    description = "The AI remembers the last 5 cards it has seen."
    ai_memory_size = 5
