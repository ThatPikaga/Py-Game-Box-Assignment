# ======[ M E M O R Y   —   2   P L A Y E R ]======

from src.core.constants import * # Colours
from .common import MemoryBaseMode, STATE_GAME_OVER

class Memory2PMode(MemoryBaseMode):
    menu_title = "MEMORY MATCH — 2 PLAYERS"

    def __init__(self):
        super().__init__("Memory 2 Players")
        self.current_turn = 1
        self.p1_pairs = 0
        self.p2_pairs = 0

    def _on_startup_reset(self):
        self.current_turn = 1
        self.p1_pairs = 0
        self.p2_pairs = 0

    def _on_start_game(self, config):
        self.current_turn = 1
        self.p1_pairs = 0
        self.p2_pairs = 0

    def _on_match(self):
        if self.current_turn == 1: self.p1_pairs += 1
        else: self.p2_pairs += 1

    def _on_mismatch(self):
        self.current_turn = 2 if self.current_turn == 1 else 1

    def _check_game_over(self):
        if not self._all_matched(): return False
        self.state = STATE_GAME_OVER
        if self.p1_pairs > self.p2_pairs:
            self.winner_num = 1
            self.game_over_msg = f"Player 1 wins! ({self.p1_pairs} to {self.p2_pairs})"
        elif self.p2_pairs > self.p1_pairs:
            self.winner_num = 2
            self.game_over_msg = f"Player 2 wins! ({self.p2_pairs} to {self.p1_pairs})"
        else:
            self.winner_num = 0
            self.game_over_msg = f"It's a tie! ({self.p1_pairs} pairs each)"
        return True

    def _hud_text(self):
        return f"Turn: P{self.current_turn}  |  P1: {self.p1_pairs}  |  P2: {self.p2_pairs}  (Max: {self.num_pairs})"

    def _game_over_title_colour(self):
        if self.winner_num == 1: return COL_PLAYER
        if self.winner_num == 2: return COL_AI
        return COL_GOLD