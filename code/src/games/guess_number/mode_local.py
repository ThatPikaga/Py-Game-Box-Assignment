# ======[ G U E S S   N U M B E R   -   L O C A L   2 P ]======

import random
import pygame

from src.core.constants import (
    SCREEN_WIDTH, COL_TEXT, COL_TEXT_MUTED, COL_WIN, COL_LOSE, COL_AI,
    COL_CARD_BG, COL_CARD_BORDER, title_font, header_font, body_font
)
from .common import (
    GuessNumBaseMode, GuessNumUI, 
    STATE_PLAYING, STATE_COIN_FLIP, STATE_SETTING_NUM,
    GUESS_MIN, GUESS_MAX
)

class GuessNumLocalMode(GuessNumBaseMode):
    """Two players on one keyboard - one picks, the other guesses."""
    
    title_text = "Number Guesser - Local 2P"
    name = "Guess Number Local 2P"
    
    def __init__(self):
        super().__init__()
        self.chooser_name = ""
        self.guesser_name = ""
        self.chooser_is_p1 = True
        self.coin_flip_time = 0
        
    def _on_startup_reset(self):
        self.chooser_name = ""
        self.guesser_name = ""
        self.chooser_is_p1 = True
        self.coin_flip_time = 0
        
    def _on_difficulty_chosen(self, tries):
        self.max_tries = tries
        self.tries_left = tries
        self.input_text = ""
        self.status_message = "Flipping a coin to see who picks the number..."
        self.state = STATE_COIN_FLIP
        self.coin_flip_time = pygame.time.get_ticks()
        
    def _is_typing_state(self):
        return self.state in (STATE_PLAYING, STATE_SETTING_NUM)
        
    def _on_enter_pressed(self):
        if self.state == STATE_SETTING_NUM:
            self._submit_secret_number()
        elif self.state == STATE_PLAYING:
            guess = self._validate_and_get_guess()
            if guess is not None:
                self._process_guess(guess)
                
    def _submit_secret_number(self):
        if not self.input_text:
            self.status_message = f"{self.chooser_name}, type a number first!"
            return
            
        try:
            num = int(self.input_text)
        except ValueError:
            self.input_text = ""
            return
            
        if num < GUESS_MIN or num > GUESS_MAX:
            self.status_message = f"Number must be between {GUESS_MIN} and {GUESS_MAX}. Try again."
            self.input_text = ""
            return
            
        self.secret_number = num
        self.tries_left = self.max_tries
        self.input_text = ""
        self.status_message = f"Number locked! {self.guesser_name}, it's your turn to guess."
        self.state = STATE_PLAYING
        
    def _on_correct_guess(self, guess):
        self.status_message = f"{self.guesser_name} guessed {guess} - that's it! {self.guesser_name} wins!"
        
    def _on_out_of_tries(self):
        self.status_message = f"Out of tries! The secret number was {self.secret_number}. {self.chooser_name} wins this round!"
        
    def update(self, dt):
        if self.state == STATE_COIN_FLIP:
            if pygame.time.get_ticks() - self.coin_flip_time >= 1500:
                self._resolve_coin_flip()
                
    def _resolve_coin_flip(self):
        self.chooser_is_p1 = random.choice([True, False])
        if self.chooser_is_p1:
            self.chooser_name = "Player 1"
            self.guesser_name = "Player 2"
        else:
            self.chooser_name = "Player 2"
            self.guesser_name = "Player 1"
            
        self.status_message = f"{'Heads' if self.chooser_is_p1 else 'Tails'}! {self.chooser_name} picks the secret number."
        self.input_text = ""
        self.state = STATE_SETTING_NUM
        
    def _draw_gameplay(self, surface):
        if self.state == STATE_COIN_FLIP:
            self._draw_coin_flip(surface)
        elif self.state == STATE_SETTING_NUM:
            self._draw_setting_number(surface)
        elif self.state == STATE_PLAYING:
            self._draw_playing(surface)
            
    def _draw_coin_flip(self, surface):
        card = pygame.Rect(30, 110, SCREEN_WIDTH - 60, 100)
        pygame.draw.rect(surface, COL_CARD_BG, card, border_radius=12)
        pygame.draw.rect(surface, COL_CARD_BORDER, card, width=2, border_radius=12)
        
        msg = header_font().render(self.status_message, True, COL_TEXT)
        surface.blit(msg, (card.x + 25, card.y + 32))
        
    def _draw_setting_number(self, surface):
        card = pygame.Rect(30, 100, SCREEN_WIDTH - 60, 140)
        pygame.draw.rect(surface, COL_CARD_BG, card, border_radius=12)
        pygame.draw.rect(surface, COL_AI, card, width=2, border_radius=12)
        
        who = title_font().render(f"{self.chooser_name}: pick a secret number!", True, COL_AI)
        surface.blit(who, (card.x + 25, card.y + 18))
        
        warn = body_font().render(f"Oi! {self.guesser_name}, look away! No peeking!", True, COL_LOSE)
        surface.blit(warn, (card.x + 25, card.y + 65))
        
        hint = body_font().render("The number will be hidden as ****", True, COL_TEXT_MUTED)
        surface.blit(hint, (card.x + 25, card.y + 100))
        
        input_box = pygame.Rect(40, 325, 200, 50)
        GuessNumUI.draw_input_box(surface, input_box, "Type a number (1-1000) and press Enter:", self.input_text, hidden=True)
        
    def _draw_playing(self, surface):
        card = pygame.Rect(30, 100, SCREEN_WIDTH - 60, 140)
        pygame.draw.rect(surface, COL_CARD_BG, card, border_radius=12)
        pygame.draw.rect(surface, COL_CARD_BORDER, card, width=2, border_radius=12)
        
        turn = header_font().render(f"{self.guesser_name} is guessing", True, COL_TEXT)
        surface.blit(turn, (card.x + 25, card.y + 18))
        
        tries_text = body_font().render(f"Tries left: {self.tries_left} / {self.max_tries}", True, COL_TEXT)
        surface.blit(tries_text, (card.x + 25, card.y + 58))
        
        status_color = COL_WIN if "win" in self.status_message.lower() else COL_TEXT_MUTED
        status_surf = body_font().render(self.status_message, True, status_color)
        surface.blit(status_surf, (card.x + 25, card.y + 95))
        
        input_box = pygame.Rect(40, 320, 200, 50)
        GuessNumUI.draw_input_box(surface, input_box, "Type your guess:", self.input_text)

    def _draw_game_over(self, surface):
        card = pygame.Rect(30, 100, SCREEN_WIDTH - 60, 180)
        pygame.draw.rect(surface, COL_CARD_BG, card, border_radius=12)
        pygame.draw.rect(surface, COL_CARD_BORDER, card, width=2, border_radius=12)
        
        outcome = title_font().render(self.status_message, True, COL_WIN)
        surface.blit(outcome, (card.x + 25, card.y + 30))
        
        detail = body_font().render(
            f"{self.chooser_name} chose the number that {self.guesser_name} was guessing", 
            True, COL_TEXT_MUTED
        )
        surface.blit(detail, (card.x + 25, card.y + 90))
        
        reveal = body_font().render(f"The secret number was: {self.secret_number}", True, COL_TEXT)
        surface.blit(reveal, (card.x + 25, card.y + 130))