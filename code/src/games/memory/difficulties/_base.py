# These are the shared defaults for every Memory difficulty.
# Only the AI cares about these - Single player and local vs never read them.

from src.core.difficulty_base import Difficulty

class MemoryDifficulty(Difficulty):
    # -- AI memory --
    # How many face-up sightings the AI can hold in its head at once.
    # Every card that gets flipped (by the player OR the AI) counts as one
    # sighting. Once the AI is holding more than this, it forgets the
    # oldest sighting first. Cards that get matched are thrown out straight
    # away because there's no point remembering them.
    # e.g. 2 = the AI only remembers the last 2 cards it saw
    ai_memory_size = 4
