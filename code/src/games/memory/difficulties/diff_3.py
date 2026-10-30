# Hard - 52 pairs on the board (104 cards).
# Huge board, but the AI can hold onto the last 8 cards it has seen.
# It still forgets older cards, so it's not a perfect robot, but it
# will punish you if you flip a card it already knows the partner of.

from src.games.memory.difficulties._base import MemoryDifficulty

class Difficulty(MemoryDifficulty):
    name = "Hard"
    description = "The AI remembers the last 8 cards it has seen."
    ai_memory_size = 8
