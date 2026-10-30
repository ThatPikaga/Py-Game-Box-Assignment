# guess_num_common.py

import pygame
import random

from src.core.game_base import GameBase
from src.core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, scale_x, scale_y, scale_size,
    COL_BG, COL_WHITE, COL_BLACK, COL_TEXT, COL_TEXT_MUTED,
    COL_CARD_BG, COL_CARD_BORDER, COL_GOLD, COL_WIN, COL_LOSE, COL_AI,
    title_font, header_font, body_font
)

# == Shared Constants ===============================================
GUESS_MIN = 1
GUESS_MAX = 1000
MAX_INPUT_LEN = 4

GUESS_DIFFICULTIES = [
    ("Easy", 20),
    ("Medium", 10),
    ("Hard", 5),
]

DIFF_BTN_W = scale_x(200)
DIFF_BTN_H = scale_y(60)
DIFF_BTN_GAP = scale_x(30)
DIFF_BTN_BASE_Y = scale_y(300)

BACK_BTN_W = scale_x(200)
BACK_BTN_H = scale_y(50)

# == States =========================================================
STATE_MENU = "MENU_DIFFICULTY"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"
STATE_COIN_FLIP = "COIN_FLIP"
STATE_SETTING_NUM = "SETTING_NUM"


# == Shared UI Drawing ==============================================
class GuessNumUI:
    """Static helper methods for drawing the Number Guesser UI."""
    
    @staticmethod
    def draw_title_bar(surface, title_text):
        bar = pygame.Rect(scale_x(20), scale_y(15), SCREEN_WIDTH - scale_x(40), scale_y(60))
        pygame.draw.rect(surface, COL_CARD_BG, bar, border_radius=10)
        pygame.draw.rect(surface, COL_CARD_BORDER, bar, width=2, border_radius=10)
        
        # Using COL_GOLD as the main highlight/accent color
        title = title_font().render(title_text, True, COL_GOLD)
        surface.blit(title, (bar.x + scale_x(20), bar.y + scale_y(10)))

    @staticmethod
    def draw_difficulty_menu(surface, diff_buttons):
        prompt = header_font().render("Choose your difficulty:", True, COL_TEXT)
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, scale_y(220)))
        surface.blit(prompt, prompt_rect)

        for btn in diff_buttons:
            rect = btn["rect"]
            pygame.draw.rect(surface, COL_CARD_BG, rect, border_radius=10)
            pygame.draw.rect(surface, COL_CARD_BORDER, rect, width=2, border_radius=10)

            lbl = header_font().render(btn["label"], True, COL_GOLD)
            sub = body_font().render(f"{btn['tries']} tries", True, COL_TEXT_MUTED)
            
            surface.blit(lbl, (rect.centerx - lbl.get_width() // 2, rect.y + scale_y(8)))
            surface.blit(sub, (rect.centerx - sub.get_width() // 2, rect.y + scale_y(34)))

    @staticmethod
    def draw_input_box(surface, rect, prompt_text, input_text, hidden=False):
        prompt = header_font().render(prompt_text, True, COL_TEXT)
        surface.blit(prompt, (rect.x, rect.y - scale_y(40)))

        pygame.draw.rect(surface, COL_CARD_BG, rect, border_radius=8)
        pygame.draw.rect(surface, COL_CARD_BORDER, rect, width=2, border_radius=8)

        display_str = "*" * len(input_text) if hidden else input_text
        text_col = COL_GOLD if hidden else COL_TEXT
        display_text = header_font().render(display_str, True, text_col)
        surface.blit(display_text, (rect.x + scale_x(14), rect.y + scale_y(12)))

        # Blinking cursor
        if pygame.time.get_ticks() % 1000 < 500:
            cursor_x = rect.x + scale_x(14) + display_text.get_width() + scale_x(4)
            if cursor_x < rect.right - scale_x(10):
                pygame.draw.line(
                    surface, COL_WHITE,
                    (cursor_x, rect.y + scale_y(12)),
                    (cursor_x, rect.y + scale_y(38)),
                    2,
                )
                
    @staticmethod
    def draw_back_button(surface, back_button):
        pygame.draw.rect(surface, COL_GOLD, back_button, border_radius=8)
        back_lbl = header_font().render("Play Again", True, COL_BLACK)
        surface.blit(back_lbl, back_lbl.get_rect(center=back_button.center))


# === Base Mode ===========================
class GuessNumBaseMode(GameBase):
    title_text = "Number Guesser"
    name = "Number Guesser"  # Default fallback name
    
    def __init__(self):
        super().__init__()
        
        self.state = STATE_MENU
        self.difficulty = None
        
        self.secret_number = 0
        self.max_tries = 0
        self.tries_left = 0
        self.input_text = ""
        self.status_message = ""
        
        self._init_diff_buttons()
        
        self.back_button = pygame.Rect(
            SCREEN_WIDTH // 2 - BACK_BTN_W // 2, scale_y(520), BACK_BTN_W, BACK_BTN_H
        )
        
    def _init_diff_buttons(self):
        total_w = len(GUESS_DIFFICULTIES) * DIFF_BTN_W + (len(GUESS_DIFFICULTIES) - 1) * DIFF_BTN_GAP
        start_x = (SCREEN_WIDTH - total_w) // 2
        
        self.diff_buttons = []
        for label, tries in GUESS_DIFFICULTIES:
            x = start_x + len(self.diff_buttons) * (DIFF_BTN_W + DIFF_BTN_GAP)
            self.diff_buttons.append({
                "rect": pygame.Rect(x, DIFF_BTN_BASE_Y, DIFF_BTN_W, DIFF_BTN_H),
                "label": label,
                "tries": tries,
            })
            
    def startup(self, persist):
        super().startup(persist)
        self.state = STATE_MENU
        self.input_text = ""
        self.status_message = ""
        self._on_startup_reset()
        # The shared difficulty screen passes a choice in before startup.
        # When that happens, there is no need to show the old second menu.
        if self.difficulty is not None:
            tries = getattr(self.difficulty, "max_tries", 10)
            self._on_difficulty_chosen(tries)
        
    def _on_startup_reset(self):
        pass
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.pause_requested = True
            return None

        if self.state == STATE_GAME_OVER and event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_e):
                return "PLAY_AGAIN"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.state == STATE_MENU:
                for btn in self.diff_buttons:
                    if btn["rect"].collidepoint(pos):
                        self._on_difficulty_chosen(btn["tries"])
                        return None
            elif self.state == STATE_GAME_OVER:
                if self.back_button.collidepoint(pos):
                    return "PLAY_AGAIN"
                    
        if event.type == pygame.KEYDOWN and self._is_typing_state():
            self._handle_keyboard_input(event)
            
        return None
        
    def _is_typing_state(self):
        return self.state == STATE_PLAYING
        
    def _handle_keyboard_input(self, event):
        if event.key == pygame.K_RETURN:
            self._on_enter_pressed()
        elif event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
        elif event.unicode.isdigit() and len(self.input_text) < MAX_INPUT_LEN:
            self.input_text += event.unicode
            
    def _on_enter_pressed(self):
        pass
        
    def _on_difficulty_chosen(self, tries):
        pass
        
    def _validate_and_get_guess(self):
        if not self.input_text:
            return None
        try:
            guess = int(self.input_text)
        except ValueError:
            self.input_text = ""
            return None
            
        if guess < GUESS_MIN or guess > GUESS_MAX:
            self.status_message = f"Out of range! Guess between {GUESS_MIN} and {GUESS_MAX} (you typed {guess})."
            self.input_text = ""
            return None
            
        return guess

    def _process_guess(self, guess):
        self.tries_left -= 1
        
        if guess == self.secret_number:
            self._on_correct_guess(guess)
            self.state = STATE_GAME_OVER
            self.input_text = ""
            self._play_sfx("num_correct")
            return True
            
        if guess < self.secret_number:
            self.status_message = f"{guess} is too LOW! Aim higher."
            self._play_sfx("num_wrong")
        else:
            self.status_message = f"{guess} is too HIGH! Come on down."
            self._play_sfx("num_wrong")
            
        if self.tries_left == 0:
            self._on_out_of_tries()
            self.state = STATE_GAME_OVER
            self.input_text = ""
            return True
            
        self.input_text = ""
        return False

    def _on_correct_guess(self, guess):
        pass
        
    def _on_out_of_tries(self):
        pass
        
    def _play_sfx(self, key):
        if key in self.sfx:
            try:
                self.sfx[key].play()
            except Exception:
                pass

    def update(self, dt):
        pass
        
    def draw(self, surface):
        surface.fill(COL_BG)
        GuessNumUI.draw_title_bar(surface, self.title_text)
        
        if self.state == STATE_MENU:
            GuessNumUI.draw_difficulty_menu(surface, self.diff_buttons)
        elif self.state == STATE_GAME_OVER:
            self._draw_game_over(surface)
            GuessNumUI.draw_back_button(surface, self.back_button)
        else:
            self._draw_gameplay(surface)
            
    def _draw_gameplay(self, surface):
        pass
        
    def _draw_game_over(self, surface):
        pass
        
    def cleanup(self):
        pass