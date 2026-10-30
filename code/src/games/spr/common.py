# ======[ S P R   —   C O M M O N ]======
# Shared constants, helpers, and base class for all SPR modes.
# Instead of duplicating the evaluation logic, choice mappings,
# and drawing helpers across mode_ai.py and mode_2p.py,
# we put it all here.

import pygame
import random
from src.core.game_base import GameBase
from src.core.constants import *

# ===== SPR Rules ============================

CHOICES = ["Scissors", "Paper", "Rock"]

# P1 key mapping (shared by both modes)
P1_KEYS = {
    pygame.K_a: "Scissors",
    pygame.K_w: "Paper",
    pygame.K_d: "Rock",
}

# P2 key mapping (shared by both modes)
P2_KEYS = {
    pygame.K_LEFT: "Scissors",
    pygame.K_UP:   "Paper",
    pygame.K_RIGHT: "Rock",
}

BEATS = {
    "Scissors": "Paper",
    "Paper": "Rock",
    "Rock": "Scissors",
}


def evaluate_round(c1, c2, p1_label="Player 1", p2_label="Player 2"):
    """
    Evaluate an SPR round.
    Returns (winner_message, detail_message).
    Winner message is one of:
      "Player 1 Wins!", "{p2_label} Wins!", "It's a Draw!"
    """
    if c1 == c2:
        return ("It's a Draw!", f"Both chose {c1}.")

    if BEATS[c1] == c2:
        return (f"{p1_label} Wins!", f"{c1} beats {c2}.")
    else:
        return (f"{p2_label} Wins!", f"{c2} beats {c1}.")


def random_ai_choice():
    """Pick a random SPR choice for the AI."""
    return random.choice(CHOICES)


# == Drawing helpers ==================================================

def draw_title_bar(surface, title="Scissors  Paper  Rock",
                   subtitle=None, title_colour=COL_YELLOW,
                   subtitle_colour=COL_TEXT_MUTED):
    title_surf = title_font().render(title, True, title_colour)
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, scale_y(60)))
    surface.blit(title_surf, title_rect)

    if subtitle:
        sub_surf = body_font().render(subtitle, True, subtitle_colour)


def draw_main_card(surface, w=None, h=None):
    """Draw the main game card background rect and return it."""
    w = scale_x(700) if w is None else w
    h = scale_y(420) if h is None else h
    card = pygame.Rect(SCREEN_WIDTH // 2 - w // 2, scale_y(140), w, h)
    pygame.draw.rect(surface, COL_CARD_BG, card, border_radius=12)
    return card


def draw_game_over_results(surface, card, p1_choice, p2_choice,
                           winner_text, detail_text,
                           p1_label="Player 1", p2_label="Player 2",
                           p1_colour=COL_PLAYER, p2_colour=COL_AI):
    # Winner message
    win_colour = COL_GREEN
    win_surf = header_font().render(winner_text, True, win_colour)
    win_rect = win_surf.get_rect(center=(card.centerx, card.top + scale_y(60)))
    surface.blit(win_surf, win_rect)

    # P1 choice
    p1_surf = body_font().render(f"{p1_label}:  {p1_choice}", True, p1_colour)
    p1_rect = p1_surf.get_rect(center=(card.centerx, card.top + scale_y(120)))
    surface.blit(p1_surf, p1_rect)

    # P2 choice
    p2_surf = body_font().render(f"{p2_label}:  {p2_choice}", True, p2_colour)
    p2_rect = p2_surf.get_rect(center=(card.centerx, card.top + scale_y(160)))
    surface.blit(p2_surf, p2_rect)

    # Detail
    detail_surf = body_font().render(detail_text, True, COL_TEXT_MUTED)
    detail_rect = detail_surf.get_rect(center=(card.centerx, card.top + scale_y(210)))
    surface.blit(detail_surf, detail_rect)

def draw_menu_button(surface, rect, label="Play Again",
                     bg_colour=COL_YELLOW, text_colour=COL_BLACK):
    """Draw a clickable menu button with its label centred inside."""
    pygame.draw.rect(surface, bg_colour, rect, border_radius=8)
    pygame.draw.rect(surface, COL_CARD_BORDER, rect, 2, border_radius=8)
    btn_lbl = body_font().render(label, True, text_colour)
    surface.blit(btn_lbl, btn_lbl.get_rect(center=rect.center))


# == Base Mode =========================================================

class SPRBaseMode(GameBase):
    """
    Shared base for all SPR modes.
    
    Subclasses must set:
      - self.name (e.g. "SPR 2 Players")
      - self.player_choice / self.p1_choice
      - self.ai_choice / self.p2_choice
      - self.winner_text / self.winner_text
      - self.detail_text
      - self.state
    
    Subclasses should override:
      - _handle_keydown(event) — process key presses
      - _resolve_round() — evaluate and set winner_text/detail_text
      - draw_playing(surface, card) — draw the playing state
    """

    def __init__(self):
        super().__init__()
        self.font_title = title_font()
        self.font_header = header_font()
        self.font_body = body_font()

        # Main Menu button (for GAME_OVER state)
        btn_w, btn_h = scale_x(200), scale_y(50)
        self.menu_btn = pygame.Rect(
            SCREEN_WIDTH // 2 - btn_w // 2,
            SCREEN_HEIGHT // 2 + scale_y(140),
            btn_w, btn_h,
        )

    def startup(self, persist):
        super().startup(persist)
        self.state = "PLAYING"
        self.player_choice = ""
        self.p1_choice = ""
        self.ai_choice = ""
        self.p2_choice = ""
        self.winner_text = ""
        self.detail_text = ""

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.pause_requested = True
                return None
            if self.state == "PLAYING":
                self._handle_keydown(event)
            elif self.state == "GAME_OVER" and event.key in (pygame.K_RETURN, pygame.K_e):
                return "PLAY_AGAIN"

        elif event.type == pygame.MOUSEBUTTONDOWN and self.state == "GAME_OVER":
            if self.menu_btn.collidepoint(event.pos):
                return "PLAY_AGAIN"

        return None

    def _handle_keydown(self, event):
        """Override in subclass to handle P1/P2 key presses."""
        pass

    def update(self, dt):
        pass  # SPR is event-driven, no animations

    def draw(self, surface):
        surface.fill(COL_BG)
        self._draw_title()
        card = draw_main_card(surface)
        
        if self.state == "PLAYING":
            self._draw_playing(surface, card)
        else:
            self._draw_game_over(surface, card)

    def _draw_title(self):
        """Override in subclass to draw mode-specific subtitle."""
        draw_title_bar(pygame.display.get_surface())

    def _draw_playing(self, surface, card):
        """Override to draw the playing state UI."""
        pass

    def _draw_game_over(self, surface, card):
        """Default game-over screen. Override for custom layout."""
        draw_game_over_results(
            surface, card,
            self.p1_choice or self.player_choice,
            self.p2_choice or self.ai_choice,
            self.winner_text, self.detail_text,
        )
        draw_menu_button(surface, self.menu_btn)

    def _play_sound(self, key="menu_select"):
        if key in self.sfx:
            try:
                self.sfx[key].play()
            except Exception:
                pass

    def cleanup(self):
        pass