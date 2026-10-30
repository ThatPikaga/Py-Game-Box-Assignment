# Easy - 12 pairs on the board (24 cards).
# The AI has a pretty bad memory on this one. It only holds on to the
# last 2 cards it has seen, so it forgets stuff almost straight away
# and is easy enough to beat.

from src.games.memory.difficulties._base import MemoryDifficulty

class Difficulty(MemoryDifficulty):
    name = "Easy"
    description = "The AI only remembers the last 2 cards it has seen."
    ai_memory_size = 2
