# ======[ G A M E   B A S E ]======
# every game mode inherits from this so the state machine knows
# exactly what buttons to poke without guessing

import pygame
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class GameBase:
    """
    I made this so every game mode speaks the same language.
    Instead of each game having handle_event() return strings or do
    god-knows-what, every mode has these methods and the wrapper
    treats them all the same.

    MODES — class variable that each game's __init__.py sets.
    e.g. {"1 Player": "mode_1p", "2 Players": "mode_2p"}
    """

    MODES = {}  # override in each game's __init__.py

    def __init__(self):
        self.name = "GameBase"
        self.sfx = {}
        self.persist = {}
        self.pause_requested = False   # set True when ESC wants pause

    def startup(self, persist):
        """Called when the state machine starts/resumes this mode."""
        self.persist = persist
        assets = persist.get("assets", {})
        game_name = persist.get("game_name", "")

        # A game only receives sounds from its own folder. Launcher sounds stay separate.
        self.sfx = assets.get("game_sfx", {}).get(game_name, {})
        self.pause_requested = False

    def handle_event(self, event):
        """
        Process one event. Return None (keep going) or a transition
        string like "MAIN_MENU". If ESC is pressed, set self.pause_requested
        and let the wrapper handle the pause overlay.
        """
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.pause_requested = True
        return None

    def update(self, dt):
        """dt in milliseconds."""
        pass

    def draw(self, surface):
        """Draw to the main screen surface."""
        pass

    def cleanup(self):
        """Called before switching away."""
        pass

    def get_scoreboard_data(self):
        """Optionally return a score or named metric for the scoreboard.

        Return None when the game has no number worth ranking. The launcher
        still saves that the game was played.
        """
        return None
