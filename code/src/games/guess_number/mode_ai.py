# ======[ G U E S S   N U M B E R   —   V S   A I ]======

import random
import pygame

from src.core.constants import (
    SCREEN_WIDTH, COL_TEXT, COL_TEXT_MUTED, COL_WIN, 
    COL_CARD_BG, COL_CARD_BORDER, title_font, header_font, body_font
)
from .common import (
    GuessNumBaseMode, GuessNumUI, 
    STATE_PLAYING, GUESS_MIN, GUESS_MAX
)

class GuessNumAIMode(GuessNumBaseMode):
    """The AI thinks of a number; the player types guesses to find it."""
    
    title_text = "Number Guesser - Vs AI"
    name = "Guess Number Vs AI"
    
    def __init__(self):
        super().__init__()
        
    def _on_difficulty_chosen(self, tries):
        self.max_tries = tries
        self.tries_left = tries
        self.secret_number = random.randint(GUESS_MIN, GUESS_MAX)
        self.input_text = ""
        self.status_message = f"AI has chosen a number between {GUESS_MIN} and {GUESS_MAX}. Start guessing!"
        self.state = STATE_PLAYING
        
    def _on_enter_pressed(self):
        guess = self._validate_and_get_guess()
        if guess is not None:
            self._process_guess(guess)
            
    def _on_correct_guess(self, guess):
        self.status_message = f"Boom! {guess} is right. You win!"
        
    def _on_out_of_tries(self):
        self.status_message = f"Out of tries! The secret number was {self.secret_number}. Better luck next time."
        
    def _draw_gameplay(self, surface):
        card = pygame.Rect(30, 100, SCREEN_WIDTH - 60, 140)
        pygame.draw.rect(surface, COL_CARD_BG, card, border_radius=12)
        pygame.draw.rect(surface, COL_CARD_BORDER, card, width=2, border_radius=12)
        
        tries_text = header_font().render(f"Tries left: {self.tries_left} / {self.max_tries}", True, COL_TEXT)
        surface.blit(tries_text, (card.x + 25, card.y + 18))
        
        status_color = COL_WIN if "win" in self.status_message.lower() else COL_TEXT_MUTED
        status_surf = body_font().render(self.status_message, True, status_color)
        surface.blit(status_surf, (card.x + 25, card.y + 60))
        
        hint = body_font().render(f"Hint: the number is between {GUESS_MIN} and {GUESS_MAX}.", True, COL_TEXT_MUTED)
        surface.blit(hint, (card.x + 25, card.y + 95))
        
        input_box = pygame.Rect(40, 320, 200, 50)
        GuessNumUI.draw_input_box(surface, input_box, "Type your guess:", self.input_text)

    def _draw_game_over(self, surface):
        card = pygame.Rect(30, 100, SCREEN_WIDTH - 60, 160)
        pygame.draw.rect(surface, COL_CARD_BG, card, border_radius=12)
        pygame.draw.rect(surface, COL_CARD_BORDER, card, width=2, border_radius=12)
        
        outcome = title_font().render(self.status_message, True, COL_WIN)
        surface.blit(outcome, (card.x + 25, card.y + 30))
        
        reveal = body_font().render(f"The secret number was: {self.secret_number}", True, COL_TEXT)
        surface.blit(reveal, (card.x + 25, card.y + 90))