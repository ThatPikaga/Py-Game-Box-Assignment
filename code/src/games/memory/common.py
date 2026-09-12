# memory_common.py
# Instead of having the same code coppied into each memory game mode, 
# we make it all here and call what we need inside of each mode.
# Much simpler and faster to make global edits


import pygame
import random

from src.core.game_base import GameBase
from src.core.constants import * # Colours

# == Memory Specific Settings =======================================
MEMORY_GRID_PAD_X = 12
MEMORY_GRID_PAD_Y = 12
MEMORY_GRID_START_Y = 100
MEMORY_BOTTOM_MARGIN = 40
MEMORY_SCROLL_STEP = 30

MEMORY_MATCH_DELAY_MS = 800
MEMORY_AI_DELAY_MS = 600

MEMORY_DIFFICULTIES = {
    "Easy":   {"pairs": 12, "lives": 18, "cols": 6},
    "Medium": {"pairs": 26, "lives": 31, "cols": 13},
    "Hard":   {"pairs": 52, "lives": 52, "cols": 13},
}

STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"

# == UI Layout Rects ================================================
MENU_RECT = pygame.Rect(200, 100, 600, 550)
GAME_OVER_BOX = pygame.Rect(250, 280, 500, 180)
HUD_RECT = pygame.Rect(30, 15, SCREEN_WIDTH - 60, 60)


# == Classes ========================================================
class Card:
    def __init__(self, value, index):
        self.value = value
        self.index = index
        self.is_flipped = False
        self.is_matched = False
        self.rect = pygame.Rect(0, 0, MEMORY_CARD_W, MEMORY_CARD_H)

    def draw(self, surface, x, y):
        self.rect.topleft = (x, y)

        if self.is_matched:
            bg, border, text_col = COL_DARK_GRAY, COL_LIGHT_GRAY, COL_TEXT_MUTED
        elif self.is_flipped:
            bg, border, text_col = COL_WHITE, COL_CARD_BORDER, COL_BLUE
        else:
            # Face down
            pygame.draw.rect(surface, COL_NAVY, self.rect, border_radius=3)
            pygame.draw.rect(surface, COL_BLACK, self.rect, 1, border_radius=3)
            return

        pygame.draw.rect(surface, bg, self.rect, border_radius=3)
        pygame.draw.rect(surface, border, self.rect, 2 if self.is_flipped else 1, border_radius=3)

        value_surf = body_font().render(str(self.value), True, text_col)
        surface.blit(value_surf, value_surf.get_rect(center=self.rect.center))


class MenuButton:
    def __init__(self, text, x, y, w, h, btn_type, value):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.btn_type = btn_type
        self.value = value

    def draw(self, surface, current_selection):
        is_selected = current_selection == self.value
        is_start = self.btn_type == "start"

        bg = COL_DARK_RED if is_selected or is_start else COL_BLACK
        border = COL_CARD_BORDER if is_selected else COL_DARK_GRAY

        pygame.draw.rect(surface, bg, self.rect, border_radius=4)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=4)

        text_surf = header_font().render(self.text, True, COL_WHITE)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# == Base Mode ======================================================
class MemoryBaseMode(GameBase):
    menu_title = "MEMORY MATCH"
    scroll_hint = "* Use Mouse Wheel to scroll *"

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.state = STATE_MENU
        self.selected_diff = "Easy"

        self.cards = []
        self.num_pairs = 0
        self.max_cols = 0

        self.total_grid_w = 0
        self.total_grid_h = 0
        self.grid_start_x = 0
        self.grid_start_y = MEMORY_GRID_START_Y
        self.scroll_y = 0
        self.max_scroll = 0

        self.selected_indices = []
        self.lock_board = False
        self.cooldown_timer = 0

        self.game_over_msg = ""
        self.winner_num = 0
        self._init_menu_buttons()

    def _init_menu_buttons(self):
        cx = SCREEN_WIDTH // 2
        self.menu_buttons = [
            MenuButton("Easy", cx - 230, 410, 160, 40, "diff", "Easy"),
            MenuButton("Medium", cx - 70, 410, 160, 40, "diff", "Medium"),
            MenuButton("Hard", cx + 90, 410, 160, 40, "diff", "Hard"),
            MenuButton("START GAME", cx - 90, 560, 180, 50, "start", "START"),
        ]

    def _build_deck(self):
        values = list(range(1, self.num_pairs + 1)) * 2
        random.shuffle(values)
        self.cards = [Card(value, i) for i, value in enumerate(values)]

    def _calc_grid(self):
        self.total_grid_w = self.max_cols * (MEMORY_CARD_W + MEMORY_GRID_PAD_X) - MEMORY_GRID_PAD_X
        self.grid_start_x = (SCREEN_WIDTH - self.total_grid_w) // 2
        self.grid_start_y = MEMORY_GRID_START_Y

        rows = (len(self.cards) + self.max_cols - 1) // self.max_cols
        self.total_grid_h = rows * (MEMORY_CARD_H + MEMORY_GRID_PAD_Y) + 50

        visible_bottom = SCREEN_HEIGHT - MEMORY_BOTTOM_MARGIN
        self.max_scroll = max(0, self.grid_start_y + self.total_grid_h - visible_bottom)
        self.scroll_y = 0

    def _reset_common(self):
        self.state = STATE_MENU
        self.selected_diff = "Easy"
        self.cards.clear()
        self.selected_indices.clear()
        self.lock_board = False
        self.cooldown_timer = 0
        self.scroll_y = 0
        self.max_scroll = 0
        self.game_over_msg = ""
        self.winner_num = 0

    def startup(self, persist):
        super().startup(persist)
        self._reset_common()
        self._on_startup_reset()

    def _on_startup_reset(self): pass
    def cleanup(self): pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.pause_requested = True
            return None

        if event.type != pygame.MOUSEBUTTONDOWN: return None

        if event.button == 1: self._handle_click(event.pos)
        elif event.button == 4 and self.state == STATE_PLAYING:
            self.scroll_y = max(0, self.scroll_y - MEMORY_SCROLL_STEP)
        elif event.button == 5 and self.state == STATE_PLAYING:
            self.scroll_y = min(self.max_scroll, self.scroll_y + MEMORY_SCROLL_STEP)
        return None

    def _handle_click(self, pos):
        if self.state == STATE_MENU:
            self._handle_menu_click(pos)
        elif self.state == STATE_GAME_OVER:
            self.state = STATE_MENU
        elif self.state == STATE_PLAYING and self._allow_human_click():
            self._handle_card_click(pos)

    def _handle_menu_click(self, pos):
        for button in self.menu_buttons:
            if not button.is_clicked(pos): continue
            if button.btn_type == "diff": self.selected_diff = button.value
            elif button.btn_type == "start": self._start_game()

    def _handle_card_click(self, pos):
        adjusted_pos = (pos[0], pos[1] - self.grid_start_y + self.scroll_y)
        for card in self.cards:
            if (card.rect.collidepoint(adjusted_pos) and not card.is_flipped and not card.is_matched):
                self._flip_card(card.index)
                break

    def _allow_human_click(self): return not self.lock_board

    def _start_game(self):
        config = MEMORY_DIFFICULTIES[self.selected_diff]
        self.num_pairs = config["pairs"]
        self.max_cols = config["cols"]
        self.selected_indices.clear()
        self.lock_board = False
        self.cooldown_timer = 0
        self._on_start_game(config)
        self._build_deck()
        self._calc_grid()
        self.state = STATE_PLAYING

    def _on_start_game(self, config): pass

    def _flip_card(self, idx):
        self.cards[idx].is_flipped = True
        self.selected_indices.append(idx)
        self._try_play("cardflip_up" if len(self.selected_indices) == 1 else "cardflip_down")
        if len(self.selected_indices) == 2:
            self.lock_board = True
            self.cooldown_timer = pygame.time.get_ticks() + MEMORY_MATCH_DELAY_MS

    def _try_play(self, key):
        sound = self.sfx.get(key)
        if sound:
            try: sound.play()
            except Exception: pass

    def update(self, dt):
        if self.state != STATE_PLAYING: return
        now = pygame.time.get_ticks()

        if self.lock_board and self.cooldown_timer > 0 and now >= self.cooldown_timer:
            self._evaluate_match()
            self.cooldown_timer = 0
            if not self._check_game_over():
                self._after_evaluate(now)

        if self.state == STATE_PLAYING:
            self._update_extra(now)

    def _evaluate_match(self):
        idx1, idx2 = self.selected_indices
        c1, c2 = self.cards[idx1], self.cards[idx2]

        if c1.value == c2.value:
            c1.is_matched = c2.is_matched = True
            self._on_match()
            self._try_play("num_correct")
        else:
            c1.is_flipped = c2.is_flipped = False
            self._on_mismatch()
            self._try_play("num_wrong")

        self.selected_indices.clear()
        self.lock_board = False

    def _on_match(self): pass
    def _on_mismatch(self): pass
    def _check_game_over(self): return False
    def _after_evaluate(self, now): pass
    def _update_extra(self, now): pass
    def _all_matched(self): return all(c.is_matched for c in self.cards)

    def draw(self, surface):
        if self.state == STATE_MENU: self._draw_menu(surface)
        else: self._draw_game(surface)

    def _draw_menu(self, surface):
        surface.fill(COL_BOARD_BG)
        pygame.draw.rect(surface, COL_BOARD_BG, MENU_RECT, border_radius=8)
        pygame.draw.rect(surface, COL_CARD_BORDER, MENU_RECT, 3, border_radius=8)

        title = header_font().render(self.menu_title, True, COL_GOLD)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 130)))

        info = body_font().render(f"Difficulty: {self.selected_diff}", True, COL_TEXT_MUTED)
        surface.blit(info, info.get_rect(center=(SCREEN_WIDTH // 2, 180)))

        label = header_font().render("Select Difficulty:", True, COL_WHITE)
        surface.blit(label, label.get_rect(center=(SCREEN_WIDTH // 2, 370)))

        for button in self.menu_buttons:
            current = self.selected_diff if button.btn_type == "diff" else None
            button.draw(surface, current)

    def _draw_game(self, surface):
        surface.fill(COL_BG)
        self._draw_board(surface)
        self._draw_hud(surface)
        self._draw_scroll_hint(surface)
        if self.state == STATE_GAME_OVER: self._draw_game_over(surface)

    def _draw_board(self, surface):
        game_canvas = pygame.Surface((SCREEN_WIDTH, self.total_grid_h), pygame.SRCALPHA)
        for i, card in enumerate(self.cards):
            row, col = i // self.max_cols, i % self.max_cols
            x = self.grid_start_x + col * (MEMORY_CARD_W + MEMORY_GRID_PAD_X)
            y = row * (MEMORY_CARD_H + MEMORY_GRID_PAD_Y)
            card.draw(game_canvas, x, y)
        
        visible_area = (0, self.scroll_y, SCREEN_WIDTH, SCREEN_HEIGHT - self.grid_start_y - MEMORY_BOTTOM_MARGIN)
        surface.blit(game_canvas, (0, self.grid_start_y), visible_area)

    def _draw_hud(self, surface):
        pygame.draw.rect(surface, COL_CARD_BG, HUD_RECT, border_radius=6)
        pygame.draw.rect(surface, COL_BOARD_BDR, HUD_RECT, 2, border_radius=6)
        hud = header_font().render(self._hud_text(), True, COL_TEXT)
        surface.blit(hud, hud.get_rect(center=HUD_RECT.center))

    def _hud_text(self): return ""
    def _hud_colour(self): return COL_TEXT

    def _draw_scroll_hint(self, surface):
        hint = body_font().render(self.scroll_hint, True, COL_TEXT_MUTED)
        surface.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 10)))

    def _draw_game_over(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) # Generic Black Alpha
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, COL_BOARD_BG, GAME_OVER_BOX, border_radius=6)
        pygame.draw.rect(surface, COL_CARD_BORDER, GAME_OVER_BOX, 3, border_radius=6)

        title = header_font().render("ROUND OVER", True, self._game_over_title_colour())
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, GAME_OVER_BOX.top + 25)))

        message = body_font().render(self.game_over_msg, True, COL_TEXT)
        surface.blit(message, message.get_rect(center=(SCREEN_WIDTH // 2, GAME_OVER_BOX.top + 80)))

        click_hint = body_font().render("Click anywhere to return to menu", True, COL_TEXT_MUTED)
        surface.blit(click_hint, click_hint.get_rect(center=(SCREEN_WIDTH // 2, GAME_OVER_BOX.top + 130)))

    def _game_over_title_colour(self): return COL_GOLD