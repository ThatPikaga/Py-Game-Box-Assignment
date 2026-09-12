# ======[ M E M O R Y   —   V S   A I ]======

import random
import pygame
from src.core.constants import * # Colours
from .common import MemoryBaseMode, STATE_GAME_OVER, MEMORY_AI_DELAY_MS

class MemoryAIMode(MemoryBaseMode):
    menu_title = "MEMORY MATCH — VS AI"

    def __init__(self):
        super().__init__("Memory Vs AI")
        self.current_turn = 1
        self.player_pairs = 0
        self.ai_pairs = 0
        self.ai_timer = 0

    def _on_startup_reset(self):
        self.current_turn = 1
        self.player_pairs = 0
        self.ai_pairs = 0
        self.ai_timer = 0

    def _on_start_game(self, config):
        self.current_turn = 1
        self.player_pairs = 0
        self.ai_pairs = 0
        self.ai_timer = 0

    def _allow_human_click(self):
        return not self.lock_board and self.current_turn == 1

    def _on_match(self):
        if self.current_turn == 1: self.player_pairs += 1
        else: self.ai_pairs += 1

    def _on_mismatch(self):
        self.current_turn = 2 if self.current_turn == 1 else 1

    def _check_game_over(self):
        if not self._all_matched(): return False
        self.state = STATE_GAME_OVER
        if self.player_pairs > self.ai_pairs:
            self.winner_num = 1
            self.game_over_msg = f"You win! ({self.player_pairs} to {self.ai_pairs})"
        elif self.ai_pairs > self.player_pairs:
            self.winner_num = 2
            self.game_over_msg = f"AI wins! ({self.ai_pairs} to {self.player_pairs})"
        else:
            self.winner_num = 0
            self.game_over_msg = f"It's a tie! ({self.player_pairs} pairs each)"
        return True

    def _after_evaluate(self, now):
        if self.current_turn == 2 and not self.lock_board:
            self.ai_timer = now + MEMORY_AI_DELAY_MS

    def _update_extra(self, now):
        if self.current_turn == 2 and not self.lock_board and self.ai_timer and now >= self.ai_timer:
            self._execute_ai_turn()
            self.ai_timer = 0

    def _execute_ai_turn(self):
        available = [c.index for c in self.cards if not c.is_flipped and not c.is_matched]
        if len(available) >= 2:
            first, second = random.sample(available, 2)
            self._flip_card(first)
            self._flip_card(second)

    def _hud_text(self):
        turn_name = "Your Turn" if self.current_turn == 1 else "AI's Turn"
        return f"{turn_name}  |  You: {self.player_pairs}  |  AI: {self.ai_pairs}  (Max: {self.num_pairs})"

    def _game_over_title_colour(self):
        if self.winner_num == 1: return COL_PLAYER
        if self.winner_num == 2: return COL_AI
        return COL_GOLD