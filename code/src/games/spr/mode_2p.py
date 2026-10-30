# ======[ S P R   —   2   P L A Y E R ]======
# local multiplayer on ONE keyboard — no network, no excuses, just
# two friends mashing keys and blaming the other for peeking

import pygame
from src.core.game_base import GameBase
from src.core.constants import *
from src.games.spr.common import (
    SPRBaseMode,
    P1_KEYS, P2_KEYS,
    evaluate_round,
    draw_title_bar, draw_main_card, draw_menu_button,
    draw_game_over_results,
)

class SPR2PMode(SPRBaseMode):
    """
    Two-player SPR on the same keyboard. Both players choose
    simultaneously — no turns, no symmetry advantage, just the raw
    anxiety of picking before you see the other person's move.

    Like the AI mode, this does NOT use GameKeyHandler. Why?
    Because this is NOT a real-time game where you hold a key for
    continuous movement. This is a game where you tap ONE key, get
    judged by fate, and live with the consequences. Adding held-key
    tracking and DAS to rock-paper-scissors would be like writing a
    full physics engine for a coin flip: impressive over-engineering
    that makes absolutely no difference to the outcome.
    """

    def __init__(self):
        super().__init__()
        self.name = "SPR 2 Players"

        # === state ===
        self.state = "PLAYING"
        self.p1_choice = ""
        self.p2_choice = ""
        self.winner_text = ""
        self.detail_text = ""

        # Move the menu button lower for 2P layout
        self.menu_btn = pygame.Rect(
            SCREEN_WIDTH // 2 - scale_x(100),
            SCREEN_HEIGHT // 2 + scale_y(140),
            scale_x(200), scale_y(50),
        )

    # =================================================================
    #   E V E N T S
    # =================================================================

    def _handle_keydown(self, event):
        # P1 input
        if not self.p1_choice and event.key in P1_KEYS:
            self.p1_choice = P1_KEYS[event.key]

        # P2 input
        if not self.p2_choice and event.key in P2_KEYS:
            self.p2_choice = P2_KEYS[event.key]

        # once both have locked in — let fate decide
        if self.p1_choice and self.p2_choice:
            self._resolve_round()

    # =================================================================
    #   D R A W
    # =================================================================

    def _draw_title(self):
        draw_title_bar(pygame.display.get_surface(),
                       subtitle="— 2 Players —")

    def _draw_playing(self, surface, card):
        prompt = self.font_header.render("Both players choose simultaneously:", True, COL_TEXT)
        prompt_rect = prompt.get_rect(center=(card.centerx, card.top + scale_y(40)))
        surface.blit(prompt, prompt_rect)

        # === P1 side ===
        p1_card = pygame.Rect(card.left + scale_x(30), card.top + scale_y(80), scale_x(300), scale_y(280))
        pygame.draw.rect(surface, COL_PLAYER, p1_card, border_radius=8, width=2)

        p1_hdr = self.font_header.render("Player 1", True, COL_PLAYER)
        p1_hdr_rect = p1_hdr.get_rect(center=(p1_card.centerx, p1_card.top + scale_y(25)))
        surface.blit(p1_hdr, p1_hdr_rect)

        p1_status = self.font_body.render(
            "Locked In!" if self.p1_choice else "Waiting...",
            True, COL_PLAYER if self.p1_choice else COL_TEXT_MUTED,
        )
        p1_stat_rect = p1_status.get_rect(center=(p1_card.centerx, p1_card.top + scale_y(60)))
        surface.blit(p1_status, p1_stat_rect)

        p1_hint = self.font_body.render(
            f"Choice: {self.p1_choice}" if self.p1_choice else "[A] Scissors  [W] Paper  [D] Rock",
            True, COL_TEXT,
        )
        p1_hint_rect = p1_hint.get_rect(center=(p1_card.centerx, p1_card.top + scale_y(100)))
        surface.blit(p1_hint, p1_hint_rect)

        # === P2 side ===
        p2_card = pygame.Rect(card.right - scale_x(330), card.top + scale_y(80), scale_x(300), scale_y(280))
        pygame.draw.rect(surface, COL_AI, p2_card, border_radius=8, width=2)

        p2_hdr = self.font_header.render("Player 2", True, COL_AI)
        p2_hdr_rect = p2_hdr.get_rect(center=(p2_card.centerx, p2_card.top + scale_y(25)))
        surface.blit(p2_hdr, p2_hdr_rect)

        p2_status = self.font_body.render(
            "Locked In!" if self.p2_choice else "Waiting...",
            True, COL_AI if self.p2_choice else COL_TEXT_MUTED,
        )
        p2_stat_rect = p2_status.get_rect(center=(p2_card.centerx, p2_card.top + scale_y(60)))
        surface.blit(p2_status, p2_stat_rect)

        p2_hint = self.font_body.render(
            f"Choice: {self.p2_choice}" if self.p2_choice
            else "[left] Scissors  [up] Paper  [right] Rock",
            True, COL_TEXT,
        )
        p2_hint_rect = p2_hint.get_rect(center=(p2_card.centerx, p2_card.top + scale_y(100)))
        surface.blit(p2_hint, p2_hint_rect)

        # === cross-card status ===
        if not self.p1_choice and not self.p2_choice:
            msg = "P1: press A / W / D  |  P2: press left / up / right"
            colour = COL_TEXT_MUTED
        elif not self.p1_choice:
            msg = "P2 is locked in — P1 still needs to pick!"
            colour = COL_PLAYER
        elif not self.p2_choice:
            msg = "P1 is locked in — P2 still needs to pick!"
            colour = COL_AI
        else:
            msg = "Both locked in! Revealing results..."
            colour = COL_GREEN

        status_surf = self.font_header.render(msg, True, colour)
        status_rect = status_surf.get_rect(center=(card.centerx, card.bottom - scale_y(35)))
        surface.blit(status_surf, status_rect)

    def _draw_game_over(self, surface, card):
        draw_game_over_results(
            surface, card,
            self.p1_choice, self.p2_choice,
            self.winner_text, self.detail_text,
            p1_label="Player 1", p2_label="Player 2",
        )
        draw_menu_button(surface, self.menu_btn)

    # ======[ R O U N D   L O G I C ]======

    def _resolve_round(self):
        """Both players have chosen — determine who wins, play sound."""
        c1, c2 = self.p1_choice, self.p2_choice
        self.winner_text, self.detail_text = evaluate_round(
            c1, c2, p1_label="Player 1", p2_label="Player 2",
        )
        self.state = "GAME_OVER"
        self._play_sound("menu_select")