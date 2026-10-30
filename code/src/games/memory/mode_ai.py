# ======[ M E M O R Y   --   V S   A I ]======
#
# How the AI works in this mode:
#   The AI has a little "memory" of cards it has seen face up. Every time
#   ANY card gets flipped (by the player or by the AI) it gets written into
#   that memory. The memory has a size limit that comes from the difficulty
#   (see the difficulties folder), so once it's full the AI forgets the
#   OLDEST card it was holding. Cards that have been matched get thrown out
#   straight away because there's no point remembering them anymore.
#
#   On its turn the AI will:
#     1. flip a pair it already knows about, if it remembers one
#     2. otherwise flip a card it has never seen (or has forgotten)
#     3. if that card matches something in its memory, flip the match
#     4. if not, flip another unknown card and hope for the best

import random
import importlib
import pygame
from src.core.constants import * # Colours
from .common import MemoryBaseMode, STATE_GAME_OVER, MEMORY_AI_DELAY_MS
from .difficulties import DIFFICULTIES

# Used if a difficulty file can't be found / doesn't set a memory size,
# so the AI still works instead of crashing
DEFAULT_AI_MEMORY_SIZE = 4

class MemoryAIMode(MemoryBaseMode):
    menu_title = "MEMORY MATCH — VS AI"

    def __init__(self):
        super().__init__("Memory Vs AI")

        # Same idea as pong - if something attaches a difficulty object to
        # us before the game starts we'll use it. If not (None) we just use
        # whichever difficulty button was picked on the memory menu.
        self.difficulty = None

        self.current_turn = 1
        self.player_pairs = 0
        self.ai_pairs = 0
        self.ai_timer = 0

        # The AI's brain. It's a dict of {card index: card value}.
        # Dicts keep the order things were added in, so the FIRST item is
        # always the card the AI saw longest ago (the one it forgets first).
        self.ai_memory = {}
        self.ai_memory_size = DEFAULT_AI_MEMORY_SIZE

    # == setting up / resetting ==

    def _reset_ai_state(self):
        """Puts the turn, scores and the AI's memory back to the start."""
        self.current_turn = 1
        self.player_pairs = 0
        self.ai_pairs = 0
        self.ai_timer = 0
        self.ai_memory.clear()

    def _on_startup_reset(self):
        self._reset_ai_state()

    def _on_start_game(self, config):
        self._reset_ai_state()
        # work out how good the AI's memory is for the difficulty picked
        self.ai_memory_size = self._load_ai_memory_size()

    def _load_ai_memory_size(self):
        """Finds how many cards the AI is allowed to remember."""
        # 1) a difficulty object was attached from outside (like pong does)
        if self.difficulty is not None:
            return getattr(self.difficulty, "ai_memory_size", DEFAULT_AI_MEMORY_SIZE)

        # 2) otherwise look up the difficulty that matches the menu button
        #    (Easy/Medium/Hard) in difficulties/__init__.py and load its file
        module_name = DIFFICULTIES.get(self.selected_diff)
        if module_name is None:
            return DEFAULT_AI_MEMORY_SIZE

        module = importlib.import_module(f".difficulties.{module_name}", package=__package__)
        return getattr(module.Difficulty, "ai_memory_size", DEFAULT_AI_MEMORY_SIZE)

    # == player interaction ==

    def _allow_human_click(self):
        return not self.lock_board and self.current_turn == 1

    # == AI memory ==

    def _on_card_seen(self, idx):
        """
        Gets called (from common.py) every time a card is flipped face up,
        no matter who flipped it. This is how the AI "watches" the player.
        """
        # if the AI already remembers this card, remove the old entry first.
        # Adding it again puts it at the back of the line (most recent)
        # instead of listing the same card twice.
        self.ai_memory.pop(idx, None)
        self.ai_memory[idx] = self.cards[idx].value

        # memory too full? forget the oldest cards until it fits again
        while len(self.ai_memory) > self.ai_memory_size:
            oldest_idx = next(iter(self.ai_memory))
            del self.ai_memory[oldest_idx]

    def _find_known_pair(self):
        """
        Looks through the AI's memory for two different cards with the same
        value. Returns (index1, index2) if it finds one, otherwise None.
        """
        first_seen = {}  # value -> index of the first card we saw with it
        for idx, value in self.ai_memory.items():
            if value in first_seen:
                return first_seen[value], idx
            first_seen[value] = idx
        return None

    # == game rules ==

    def _on_match(self):
        # The pair is done, so the AI forgets both cards. (selected_indices
        # still holds the two matched cards at this point - common.py only
        # clears it AFTER calling this.)
        for idx in self.selected_indices:
            self.ai_memory.pop(idx, None)

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

    # == AI turn ==

    def _after_evaluate(self, now):
        if self.current_turn == 2 and not self.lock_board:
            self.ai_timer = now + MEMORY_AI_DELAY_MS

    def _update_extra(self, now):
        if self.current_turn == 2 and not self.lock_board and self.ai_timer and now >= self.ai_timer:
            self._execute_ai_turn()
            self.ai_timer = 0

    def _execute_ai_turn(self):
        # every card that's still face down and hasn't been matched
        available = [c.index for c in self.cards if not c.is_flipped and not c.is_matched]
        if len(available) < 2:
            return

        # Step 1: does the AI already remember where a pair is? Easy points!
        known_pair = self._find_known_pair()
        if known_pair:
            self._flip_card(known_pair[0])
            self._flip_card(known_pair[1])
            return

        # Take a copy of what the AI knew at the start of its turn. Flipping
        # a card adds it to the real memory, which could push an old card
        # out the back before the AI gets to use it. Looking at this copy
        # means the AI finishes its turn with the knowledge it started with
        # (plus the new card it just flipped over).
        remembered_before = dict(self.ai_memory)

        # Step 2: flip a card the AI has no memory of. If somehow every card
        # left is one it remembers, just pick any of them.
        unknown_cards = [i for i in available if i not in remembered_before]
        first = random.choice(unknown_cards) if unknown_cards else random.choice(available)
        self._flip_card(first)
        first_value = self.cards[first].value

        # Step 3: does the card it just flipped match anything it remembers?
        for idx, value in remembered_before.items():
            if value == first_value and idx != first:
                self._flip_card(idx)
                return

        # Step 4: no idea where the partner is, so flip another unknown card.
        # (Known cards are skipped because the AI already knows they can't
        # match the first card, otherwise step 3 would have caught it.)
        unknown_cards = [i for i in available if i not in remembered_before and i != first]
        if unknown_cards:
            second = random.choice(unknown_cards)
        else:
            second = random.choice([i for i in available if i != first])
        self._flip_card(second)

    # == drawing ==

    def _hud_text(self):
        turn_name = "Your Turn" if self.current_turn == 1 else "AI's Turn"
        return f"{turn_name}  |  You: {self.player_pairs}  |  AI: {self.ai_pairs}  (Max: {self.num_pairs})"

    def _game_over_title_colour(self):
        if self.winner_num == 1: return COL_PLAYER
        if self.winner_num == 2: return COL_AI
        return COL_GOLD
