# ======[ I N P U T   H A N D L E R ]======
# fixed the whole "hold W then press S doesn't work because we check
# keydown not what's currently held" problem.
#
# The trick: track held keys with a list (ordered by press time).
# When you press a new key while another is held, the list gives us
# the most recent one as the "active" key.  When you release, we
# fall back to whatever's still held.
#
# Also handles DAS (Delayed Auto-Shift) for NES Tetris-style held-repeat.

import pygame
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

# ========================= Arcade-style action map ========================================
# maps logical actions to physical keys - easy to remap later
_ACTION_MAP = {
    "MOVE_UP":      pygame.K_UP,
    "MOVE_DOWN":    pygame.K_DOWN,
    "MOVE_LEFT":    pygame.K_LEFT,
    "MOVE_RIGHT":   pygame.K_RIGHT,
    "CONFIRM":      pygame.K_e,
    "BACK":         pygame.K_ESCAPE,
    "SCORES":       pygame.K_t,
    "SETTINGS":     pygame.K_s,
    "ENTER":        pygame.K_RETURN,
}

class KeyTracker:
    """
    Tracks held keys as an ordered list so the "most recent" held
    key determines the active direction.
    
    Usage:
        tracker = KeyTracker()
        # in event loop:
        tracker.handle_event(event)
        # in update:
        active = tracker.get_active()
        if active == "MOVE_LEFT": ...
    """

    def __init__(self):
        # ordered list of action names currently held; most recent at the end
        self._held_actions = []
        # last-pressed timestamp per action (for DAS)
        self._press_times = {}

    def handle_event(self, event):
        """Call this from your event loop with each KEYDOWN/KEYUP."""
        if event.type == pygame.KEYDOWN:
            action = self._key_to_action(event.key)
            if action:
                # remove then re-add so it becomes most recent
                if action in self._held_actions:
                    self._held_actions.remove(action)
                self._held_actions.append(action)
                self._press_times[action] = pygame.time.get_ticks()
                return action  # useful for one-shot triggers

        elif event.type == pygame.KEYUP:
            action = self._key_to_action(event.key)
            if action and action in self._held_actions:
                self._held_actions.remove(action)
            return None

        return None

    def get_active(self):
        """Return the most recently pressed action that's still held."""
        if self._held_actions:
            return self._held_actions[-1]
        return None

    def is_held(self, action):
        """Check if a specific action is currently held."""
        return action in self._held_actions

    def get_das_repeat(self, action, delay=170, repeat=50):
        """
        DAS check: returns True once on initial press, then again every
        `repeat` ms after `delay` ms of holding.
        """
        if not self.is_held(action):
            return False
        elapsed = pygame.time.get_ticks() - self._press_times.get(action, 0)
        if elapsed < delay:
            return False
        # after the delay, repeat every `repeat` ms
        return (elapsed - delay) % repeat < 20

    def clear(self):
        """Reset everything - use when switching states."""
        self._held_actions.clear()
        self._press_times.clear()

    def _key_to_action(self, key):
        """Reverse lookup: pygame key constant → action name."""
        for action, k in _ACTION_MAP.items():
            if k == key:
                return action
        return None


# ========================= Game-specific key maps =========================================
# Each game has its own logical keys; the handler maps them generically

GAME_KEY_MAPS = {
    "pong": {
        # P1 uses W/S for up/down
        "P1_UP":    pygame.K_w,
        "P1_DOWN":  pygame.K_s,
    },
    "breakout": {
        "P1_LEFT":  pygame.K_LEFT,
        "P1_RIGHT": pygame.K_RIGHT,
        # also map A/D for lefties
        "P1_LEFT_ALT":  pygame.K_a,
        "P1_RIGHT_ALT": pygame.K_d,
    },
    "tetris_p2": {
        "LEFT":    pygame.K_LEFT,
        "RIGHT":   pygame.K_RIGHT,
        "DOWN":    pygame.K_DOWN,
        "ROTATE":  pygame.K_UP,
        "DROP":    pygame.K_RSHIFT,
    },
    "tetris_p1": {
        "LEFT":    pygame.K_a,
        "RIGHT":   pygame.K_d,
        "DOWN":    pygame.K_s,
        "ROTATE":  pygame.K_w,
        "DROP":    pygame.K_SPACE,
    },
    "spr_p1": {
        "SCISSORS": pygame.K_a,
        "PAPER":    pygame.K_w,
        "ROCK":     pygame.K_d,
    },
    "spr_p2": {
        "SCISSORS": pygame.K_LEFT,
        "PAPER":    pygame.K_UP,
        "ROCK":     pygame.K_RIGHT,
    },
}


class GameKeyHandler:
    """
    Game-specific input handler that maps physical keys to logical
    actions per game.  Each game mode creates one of these with its
    key mapping dict.
    
    Key advantage: separates "what key was pressed" from "what it means"
    so games don't all have their own ad-hoc KEYDOWN checks.
    """

    def __init__(self, key_map):
        """
        key_map = {"MOVE_UP": pygame.K_UP, "MOVE_DOWN": pygame.K_DOWN, ...}
        """
        self.reverse_map = {v: k for k, v in key_map.items()}
        self._held = {}          # {action: timestamp}
        self._held_keys = []     # ordered list for "most recent" logic
        self.key_map = key_map

    def handle_event(self, event):
        """
        Process a KEYDOWN/KEYUP.
        Returns the action name on press, or None.
        """
        if event.type == pygame.KEYDOWN:
            action = self.reverse_map.get(event.key)
            if action:
                now = pygame.time.get_ticks()
                self._held[action] = now
                # move to end of the ordered list
                if action in self._held_keys:
                    self._held_keys.remove(action)
                self._held_keys.append(action)
                return action
        elif event.type == pygame.KEYUP:
            action = self.reverse_map.get(event.key)
            if action and action in self._held:
                del self._held[action]
                if action in self._held_keys:
                    self._held_keys.remove(action)
        return None

    def get_active(self):
        """Most recently pressed action still held."""
        if self._held_keys:
            return self._held_keys[-1]
        return None

    def is_pressed(self, action):
        return self._held.get(action) is not None

    def just_pressed(self, action):
        """Was this action pressed THIS frame?"""
        return None  # use the return value of handle_event instead

    def hold_time(self, action):
        """How long the action has been held (ms). Returns 0 if not held."""
        t = self._held.get(action)
        return (pygame.time.get_ticks() - t) if t else 0

    def das(self, action, delay=170, repeat=50):
        """DAS: initial delay then repeat."""
        t = self._held.get(action)
        if t is None:
            return False
        elapsed = pygame.time.get_ticks() - t
        if elapsed < delay:
            return False
        return (elapsed - delay) % repeat < 20

    def clear(self):
        self._held.clear()
        self._held_keys.clear()