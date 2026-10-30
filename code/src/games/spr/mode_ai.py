# ======[ S P R   —   V S   A I ]======
# scissors paper rock against a beautifully random AI opponent
# no score tracking, no streaks, no drama — just you, the CPU,
# and a 1-in-3 chance of cosmic humiliation

import pygame
import random
from src.core.game_base import GameBase
from src.core.constants import *
from src.games.spr.common import (
    SPRBaseMode,
    P1_KEYS, evaluate_round, random_ai_choice,
    draw_title_bar, draw_main_card, draw_menu_button,
    draw_game_over_results,
)

class SPRAIMode(SPRBaseMode):
    """
    Single-player SPR vs AI. Three keys, one winner, no excuses.

    I am deliberately NOT using GameKeyHandler here because this is a
    turn-based game where you press one key and get a result — there is
    no DAS, no held-key tracking, no 'most recent key wins' nonsense.
    Adding an input handler to rock-paper-scissors would be like putting
    a turbocharger on a bicycle: technically possible, conceptually
    unhinged, and the bike still falls over when you stop.
    """

    def __init__(self):
        super().__init__()
        self.name = "SPR Vs AI"
        self.state = "PLAYING"
        self.player_choice = ""
        self.ai_choice = ""
        self.difficulty = None

    # =================================================================
    #   E V E N T S
    # =================================================================

    def _handle_keydown(self, event):
        if event.key in P1_KEYS:
            self._play_round(P1_KEYS[event.key])

    # =================================================================
    #   D R A W
    # =================================================================

    def _draw_title(self):
        draw_title_bar(pygame.display.get_surface(),
                       subtitle="— Vs AI —")

    def _draw_playing(self, surface, card):
        prompt = self.font_header.render("Pick your weapon:", True, COL_TEXT)
        prompt_rect = prompt.get_rect(center=(card.centerx, card.top + scale_y(50)))
        surface.blit(prompt, prompt_rect)

        # draw the three choice buttons
        labels = [("A", "Scissors"), ("W", "Paper"), ("D", "Rock")]
        colours = [COL_PLAYER, COL_YELLOW, COL_AI]
        btn_w, btn_h, gap = scale_x(160), scale_y(60), scale_x(20)
        total_w = 3 * btn_w + 2 * gap
        start_x = card.centerx - total_w // 2

        for i, (key, name) in enumerate(labels):
            bx = start_x + i * (btn_w + gap)
            by = card.top + scale_y(110)
            btn_rect = pygame.Rect(bx, by, btn_w, btn_h)
            pygame.draw.rect(surface, colours[i], btn_rect, border_radius=8)

            # key hint
            hint = self.font_body.render(f"[{key}]", True, COL_BLACK)
            hint_rect = hint.get_rect(center=(btn_rect.centerx, btn_rect.centery - scale_y(10)))
            surface.blit(hint, hint_rect)

            lbl = self.font_body.render(name, True, COL_BLACK)
            lbl_rect = lbl.get_rect(center=(btn_rect.centerx, btn_rect.centery + scale_y(14)))
            surface.blit(lbl, lbl_rect)

        # status hint at the bottom of the card
        hint = self.font_body.render("Press A / W / D to make your move", True, COL_TEXT_MUTED)
        hint_rect = hint.get_rect(center=(card.centerx, card.bottom - scale_y(30)))
        surface.blit(hint, hint_rect)

    def _draw_game_over(self, surface, card):
        draw_game_over_results(
            surface, card,
            self.player_choice, self.ai_choice,
            self.winner_text, self.detail_text,
            p1_label="You picked", p2_label="AI picked",
        )
        draw_menu_button(surface, self.menu_btn)

    # ======[ R O U N D   L O G I C ]======

    def _play_round(self, player_choice):
        """Evaluate one round: player picks, AI picks, declare winner."""
        self.player_choice = player_choice
        # Higher difficulties are more likely to choose the move that beats yours.
        # Yes.. the ai is a cheater who waits for you.
        counter_chance = getattr(self.difficulty, "counter_chance", 0.0)
        if random.random() < counter_chance:
            winning_moves = {"Scissors": "Rock", "Paper": "Scissors", "Rock": "Paper"}
            self.ai_choice = winning_moves[player_choice]
        else:
            self.ai_choice = random_ai_choice()

        self.winner_text, self.detail_text = evaluate_round(
            self.player_choice, self.ai_choice,
            p1_label="You", p2_label="AI",
        )

        self.state = "GAME_OVER"
        self._play_sound("menu_select")