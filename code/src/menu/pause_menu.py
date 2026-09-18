# ======[ P A U S E   M E N U ]======
# shared overlay that any game can pop up when you hit ESC
# Q to quit to main menu, S for settings, & ESC to resume

import pygame
from src.core.constants import *

class PauseMenu:
    """
    This isn't a full state machine state. It is a translucent overlay
    that gets drawn on top of whatever game is running. The wrapper
    handles the event routing before the game sees anything.
    """

    def __init__(self):
        self.active = False
        self.font_title = pygame.font.Font(None, FONT_TITLE_SIZE)
        self.font_body = pygame.font.Font(None, FONT_BODY_SIZE)

        # labels so I can adjust positioning in one spot
        self.options = [
            ("ESC",    "Resume"),
            ("Q",      "Quit to Menu"),
            ("S",      "Settings"),
        ]

    def open(self):
        """Show the pause overlay."""
        self.active = True

    def close(self):
        """resume the game."""
        self.active = False

    def handle_key(self, key, game_name=None):
        """
        Process pause-specific keys.
        Returns None (stay paused), "RESUME", "MAIN_MENU", or "SETTINGS".
        """
        if key == pygame.K_ESCAPE:
            return "RESUME"
        elif key == pygame.K_q:
            return "MAIN_MENU"
        elif key == pygame.K_s:
            # Return SETTINGS with game context
            return ("SETTINGS", game_name)
        return None

    def draw(self, surface):
        """Draw the semi-transparent overlay over the frozen game."""
        if not self.active:
            return

        w, h = surface.get_size()

        # dim the whole screen
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # ── pause header ──
        title = self.font_title.render("PAUSED", True, COL_YELLOW)
        surface.blit(title, (w // 2 - title.get_width() // 2, h // 2 - 100))

        # ── option list ──
        for i, (key, action) in enumerate(self.options):
            txt = f"{key}  |  {action}"
            rendered = self.font_body.render(txt, True, COL_TEXT)
            x = w // 2 - rendered.get_width() // 2
            y = h // 2 - 30 + i * 40
            surface.blit(rendered, (x, y))