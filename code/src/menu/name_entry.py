# name_entry.py — Username input screen before launching a game
# Appears after game selection, before mode select (if game has modes)
# Max 12 characters, saves to persist for stat tracking

import pygame
from src.core.constants import *

class NameEntryScreen:
# Simple text input screen that asks for player name before launching a game.
# This name is used for stat tracking and leaderboard entries.

    def __init__(self, game_name):
        self.game_name = game_name
        self.username = ""
        self.max_length = 12
        self.done = False
        self.next_state = None  # Will be "MODE_SELECT" or the game mode object

        self.font_title = title_font()
        self.font_body = body_font()
        self.font_small = make_font(14)
        self.font_error = body_font()

        # Input box
        self.input_rect = pygame.Rect(SCREEN_WIDTH // 2 - scale_x(150), SCREEN_HEIGHT // 2 - scale_y(20), scale_x(300), scale_y(50))
        self.cursor_visible = True
        self.cursor_timer = 0

        # Confirm button
        self.confirm_btn = pygame.Rect(SCREEN_WIDTH // 2 - scale_x(80), SCREEN_HEIGHT // 2 + scale_y(60), scale_x(160), scale_y(45))

        # Error message (hidden)
        self.error_message = None
        self.error_timer = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Cancel - go back to carousel
                self.done = True
                self.next_state = "MAIN_MENU"
                return

            if event.key == pygame.K_RETURN:
                # Confirm with current name (or show error if empty)
                self._confirm()
                return

            if event.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
                # Clear error message if user starts typing
                self.error_message = None
                return

            # Text input (letters, numbers, underscore, space)
            if event.unicode and len(self.username) < self.max_length:
                char = event.unicode
                if char.isalnum() or char in ('_', '', '-'):
                    self.username += char.upper()  # Store as uppercase for consistency
                    # Clear error message if user starts typing
                    self.error_message = None

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.confirm_btn.collidepoint(event.pos):
                    self._confirm()

    def _confirm(self):
        """Confirm the username and proceed."""
        if not self.username.strip():
            # Show error message if username is empty
            self.error_message = "GIVE ME A NAME YOU BAFOON!"
            return

        self.done = True
        # next_state will be set externally based on whether game has modes

    def update(self, dt):
        # Blink cursor
        self.cursor_timer += dt
        if self.cursor_timer > 500:  # Toggle every 500ms
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        # Update error message timer (clear after 1 seconds)
        if self.error_message:
            self.error_timer += dt
            if self.error_timer > 1000:
                self.error_message = None
                self.error_timer = 0

    def draw(self, surface):
        surface.fill(COL_BG)

        w, h = SCREEN_WIDTH, SCREEN_HEIGHT

        # Title
        title = self.font_title.render(f"{self.game_name}", True, COL_GOLD)
        surface.blit(title, (w // 2 - title.get_width() // 2, scale_y(150)))

        subtitle = self.font_body.render("Enter your player name", True, COL_TEXT)
        surface.blit(subtitle, (w // 2 - subtitle.get_width() // 2, scale_y(210)))

        # Input box background
        pygame.draw.rect(surface, COL_CARD_BG, self.input_rect, border_radius=8)
        pygame.draw.rect(surface, COL_GOLD if self.input_rect.collidepoint(pygame.mouse.get_pos()) else COL_CARD_BORDER,
                        self.input_rect, 3, border_radius=8)

        # Current text
        display_text = self.username
        if self.cursor_visible and len(self.username) < self.max_length:
            # Blink cursor icon
            display_text += "[]"

        text_surf = self.font_body.render(display_text, True, COL_TEXT)
        surface.blit(text_surf, (self.input_rect.x + scale_x(15), self.input_rect.centery - text_surf.get_height() // 2))

        # Character count
        count_surf = self.font_small.render(f"{len(self.username)}/{self.max_length}", True, COL_TEXT_MUTED)
        surface.blit(count_surf, (self.input_rect.right - count_surf.get_width() - scale_x(10),
                                  self.input_rect.bottom + scale_y(5)))

        # Confirm button
        pygame.draw.rect(surface, COL_DARK_RED, self.confirm_btn, border_radius=6)
        confirm_txt = self.font_body.render("CONFIRM", True, COL_WHITE)
        surface.blit(confirm_txt, (self.confirm_btn.centerx - confirm_txt.get_width() // 2,
                                   self.confirm_btn.centery - confirm_txt.get_height() // 2))

        # Error message (if any)
        if self.error_message:
            error_surf = self.font_error.render(self.error_message, True, COL_DARK_RED)
            surface.blit(error_surf, (w // 2 - error_surf.get_width() // 2, self.confirm_btn.bottom + scale_y(20)))

        # Instructions
        instr = self.font_small.render("Type your name (max 12 chars) | ENTER to confirm | ESC to cancel",
                                      True, COL_TEXT_MUTED)
        surface.blit(instr, (w // 2 - instr.get_width() // 2, h - scale_y(50)))

    def cleanup(self):
        pass
