# ======[ M E M O R Y   —   1   P L A Y E R ]======

from src.core.constants import COL_TEXT, COL_WIN, COL_LOSE
from .common import MemoryBaseMode, STATE_GAME_OVER

class Memory1PMode(MemoryBaseMode):
    menu_title = "MEMORY MATCH — Single Player"

    def __init__(self):
        super().__init__("Memory 1 Player")
        self.lives = 0
        self.pairs_found = 0

    def _on_startup_reset(self):
        self.lives = 0
        self.pairs_found = 0

    def _on_start_game(self, config):
        self.lives = config["lives"]
        self.pairs_found = 0

    def _on_match(self): self.pairs_found += 1
    def _on_mismatch(self): self.lives -= 1

    def _check_game_over(self):
        if self._all_matched():
            self.state = STATE_GAME_OVER
            self.game_over_msg = f"You win! All {self.num_pairs} pairs found with {self.lives} lives remaining!"
            return True
        if self.lives <= 0:
            self.state = STATE_GAME_OVER
            self.game_over_msg = "Game Over — you ran out of lives!"
            return True
        return False

    def _hud_text(self):
        return f"Diff: {self.selected_diff}  |  Pairs: {self.pairs_found}/{self.num_pairs}  |  Lives: {self.lives}"

    def _game_over_title_colour(self):
        return COL_WIN if self.pairs_found == self.num_pairs else COL_LOSE