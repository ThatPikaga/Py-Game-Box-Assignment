import pygame
import random
import sys

# Initialise Pygame
pygame.init()

# --- WINDOW CONFIGURATION ---
WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Match")
clock = pygame.time.Clock()

# --- COLOURS ---
COLOUR_MENU_BG = (26, 42, 58)
COLOUR_TEXT_LIGHT = (245, 230, 211)
COLOUR_WHITE = (255, 255, 255)
COLOUR_CARD_FRONT = (255, 255, 255)
COLOUR_CARD_BORDER = (217, 22, 22)

COLOUR_CARD_TEXT = (217, 22, 22)
COLOUR_MATCHED = (160, 176, 176)
COLOUR_HEADER_BG = (44, 62, 80)
COLOUR_BG_GREEN = (34, 139, 34)
COLOUR_CARD_BACK = (74, 123, 138)
COLOUR_RED = (192, 57, 43)
COLOUR_HEADER_BORDER = (196, 154, 108)

# --- FONTS ---
font_title = pygame.font.SysFont("helvetica", 36, bold=True)
font_header = pygame.font.SysFont("helvetica", 20, bold=True)
font_ui = pygame.font.SysFont("helvetica", 16, bold=True)
font_card = pygame.font.SysFont("helvetica", 22, bold=True)

# --- BACKGROUND (solid green) ---
BACKGROUND_SURFACE = pygame.Surface((WIDTH, HEIGHT))
BACKGROUND_SURFACE.fill(COLOUR_BG_GREEN)

def get_card_back_surface(w, h):
    """Return a solid retro‑teal surface for card backs."""
    surf = pygame.Surface((w, h))
    surf.fill(COLOUR_CARD_BACK)
    return surf

CARD_W, CARD_H = 55, 75
CARD_BACK_SURF = get_card_back_surface(CARD_W, CARD_H)

# --- GAME ENGINE STATE CLASSES ---
class MenuButton:
    def __init__(self, text, x, y, w, h, var_type, value):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.var_type = var_type
        self.value = value

    def draw(self, screen, current_selection):
        is_selected = current_selection == self.value
        bg_colour = (139, 90, 43) if (is_selected or self.var_type == "start") else (30, 15, 8)
        border_colour = COLOUR_CARD_BORDER if is_selected else (80, 50, 30)

        pygame.draw.rect(screen, bg_colour, self.rect, border_radius=4)
        pygame.draw.rect(screen, border_colour, self.rect, 2, border_radius=4)

        txt_surf = font_ui.render(self.text, True, COLOUR_WHITE)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Card:
    def __init__(self, value, index):
        self.value = value
        self.index = index
        self.is_flipped = False
        self.is_matched = False
        self.rect = pygame.Rect(0, 0, CARD_W, CARD_H)

    def draw(self, surface, x, y):
        self.rect.topleft = (x, y)

        if self.is_matched:
            pygame.draw.rect(surface, COLOUR_MATCHED, self.rect, border_radius=3)
            pygame.draw.rect(surface, (60, 60, 60), self.rect, 1, border_radius=3)
        elif self.is_flipped:
            pygame.draw.rect(surface, COLOUR_CARD_FRONT, self.rect, border_radius=3)
            pygame.draw.rect(surface, COLOUR_CARD_BORDER, self.rect, 2, border_radius=3)
            val_surf = font_card.render(str(self.value), True, COLOUR_CARD_TEXT)
            val_rect = val_surf.get_rect(center=self.rect.center)
            surface.blit(val_surf, val_rect)
        else:
            surface.blit(CARD_BACK_SURF, (x, y))
            pygame.draw.rect(surface, (34, 17, 5), self.rect, 1, border_radius=3)

class GameManager:
    def __init__(self):
        self.state = "MENU"
        self.selected_style = "Single Player"
        self.selected_diff = "Easy"
        self.init_menu_ui()

    def init_menu_ui(self):
        self.menu_buttons = [
            MenuButton("Single Player", 320, 220, 160, 40, "style", "Single Player"),
            MenuButton("Local VS",       500, 220, 160, 40, "style", "Local VS"),
            MenuButton("AI VS",          410, 270, 160, 40, "style", "AI VS"),
            MenuButton("Easy",           230, 410, 160, 40, "diff", "Easy"),
            MenuButton("Medium",         410, 410, 160, 40, "diff", "Medium"),
            MenuButton("Hard",           590, 410, 160, 40, "diff", "Hard"),
            MenuButton("START GAME",     400, 560, 180, 50, "start", "START"),
        ]

    def init_game_board(self):
        diff_config = {
            "Easy":   {"pairs": 12, "lives": 18, "cols": 6},
            "Medium": {"pairs": 26, "lives": 31, "cols": 13},
            "Hard":   {"pairs": 52, "lives": 52, "cols": 13},
        }
        config = diff_config[self.selected_diff]
        self.num_pairs = config["pairs"]
        self.lives = config["lives"]
        self.max_cols = config["cols"]

        self.p1_pairs = 0
        self.p2_pairs = 0
        self.current_turn = 1

        values = list(range(1, self.num_pairs + 1)) * 2
        random.shuffle(values)
        self.cards = [Card(val, i) for i, val in enumerate(values)]

        self.grid_padding_x = 12
        self.grid_padding_y = 12
        self.total_grid_w = self.max_cols * (CARD_W + self.grid_padding_x) - self.grid_padding_x
        self.grid_start_x = (WIDTH - self.total_grid_w) // 2
        self.grid_start_y = 100
        self.scroll_y = 0

        total_rows = (len(self.cards) + self.max_cols - 1) // self.max_cols
        self.total_grid_h = total_rows * (CARD_H + self.grid_padding_y) + 50
        self.max_scroll = max(0, (self.grid_start_y + self.total_grid_h) - (HEIGHT - 40))

        self.selected_indices = []
        self.lock_board = False
        self.cooldown_timer = 0
        self.ai_timer = 0
        self.game_over_msg = ""

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_click(event.pos)
                elif event.button == 4 and self.state == "PLAYING":
                    self.scroll_y = max(0, self.scroll_y - 30)
                elif event.button == 5 and self.state == "PLAYING":
                    self.scroll_y = min(self.max_scroll, self.scroll_y + 30)

    def handle_click(self, pos):
        if self.state == "MENU":
            for btn in self.menu_buttons:
                if btn.is_clicked(pos):
                    if btn.var_type == "style":
                        self.selected_style = btn.value
                    elif btn.var_type == "diff":
                        self.selected_diff = btn.value
                    elif btn.var_type == "start":
                        self.init_game_board()
                        self.state = "PLAYING"
            return

        if self.state == "GAME_OVER":
            self.state = "MENU"
            return

        if self.state == "PLAYING" and not self.lock_board:
            if self.selected_style == "AI VS" and self.current_turn == 2:
                return

            adjusted_pos = (pos[0], pos[1] - self.grid_start_y + self.scroll_y)
            for card in self.cards:
                if card.rect.collidepoint(adjusted_pos) and not card.is_flipped and not card.is_matched:
                    self.flip_card(card.index)
                    break

    def flip_card(self, idx):
        self.cards[idx].is_flipped = True
        self.selected_indices.append(idx)
        if len(self.selected_indices) == 2:
            self.lock_board = True
            self.cooldown_timer = pygame.time.get_ticks() + 800

    def update(self):
        if self.state != "PLAYING":
            return

        current_time = pygame.time.get_ticks()

        if self.lock_board and self.cooldown_timer > 0 and current_time >= self.cooldown_timer:
            self.evaluate_match()
            self.cooldown_timer = 0

            if all(c.is_matched for c in self.cards):
                self.trigger_game_over(all_cleared=True)
            elif self.selected_style == "Single Player" and self.lives <= 0:
                self.trigger_game_over(all_cleared=False)
            else:
                if self.selected_style == "AI VS" and self.current_turn == 2 and not self.lock_board:
                    self.ai_timer = current_time + 600

        if (self.selected_style == "AI VS" and self.current_turn == 2 and not self.lock_board
                and self.ai_timer > 0 and current_time >= self.ai_timer):
            self.execute_ai_turn()
            self.ai_timer = 0

    def evaluate_match(self):
        idx1, idx2 = self.selected_indices
        c1, c2 = self.cards[idx1], self.cards[idx2]

        if c1.value == c2.value:
            c1.is_matched = c2.is_matched = True
            if self.current_turn == 1:
                self.p1_pairs += 1
            else:
                self.p2_pairs += 1
        else:
            c1.is_flipped = c2.is_flipped = False
            if self.selected_style == "Single Player":
                self.lives -= 1
            else:
                self.current_turn = 2 if self.current_turn == 1 else 1

        self.selected_indices.clear()
        self.lock_board = False

    def execute_ai_turn(self):
        available = [c.index for c in self.cards if not c.is_flipped and not c.is_matched]
        if len(available) >= 2:
            choices = random.sample(available, 2)
            self.flip_card(choices[0])
            self.flip_card(choices[1])

    def trigger_game_over(self, all_cleared):
        self.state = "GAME_OVER"
        if self.selected_style == "Single Player":
            if all_cleared:
                self.game_over_msg = f"Game Over! Found all pairs with {self.lives} lives remaining!"
            else:
                self.game_over_msg = "Game Over! Out of lives!"
        else:
            p2_lbl = "AI" if self.selected_style == "AI VS" else "Player 2"
            if self.p1_pairs > self.p2_pairs:
                self.game_over_msg = f"Player 1 wins with {self.p1_pairs} pairs!"
            elif self.p2_pairs > self.p1_pairs:
                self.game_over_msg = f"{p2_lbl} wins with {self.p2_pairs} pairs!"
            else:
                self.game_over_msg = f"It's a tie! Both secured {self.p1_pairs} pairs."

    def draw(self, screen):
        screen.blit(BACKGROUND_SURFACE, (0, 0))

        if self.state == "MENU":
            menu_rect = pygame.Rect(200, 100, 600, 550)
            pygame.draw.rect(screen, COLOUR_MENU_BG, menu_rect, border_radius=8)
            pygame.draw.rect(screen, COLOUR_CARD_BORDER, menu_rect, 3, border_radius=8)

            title_surf = font_title.render("MEMORY MATCH", True, COLOUR_TEXT_LIGHT)
            screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 130)))

            lbl_style = font_header.render("Select Playstyle:", True, COLOUR_WHITE)
            screen.blit(lbl_style, lbl_style.get_rect(center=(WIDTH//2, 185)))
            lbl_diff = font_header.render("Select Difficulty:", True, COLOUR_WHITE)
            screen.blit(lbl_diff, lbl_diff.get_rect(center=(WIDTH//2, 370)))

            for btn in self.menu_buttons:
                if btn.var_type == "style":
                    current_selection = self.selected_style
                elif btn.var_type == "diff":
                    current_selection = self.selected_diff
                else:
                    current_selection = None
                btn.draw(screen, current_selection)

        elif self.state in ("PLAYING", "GAME_OVER"):
            game_canvas = pygame.Surface((WIDTH, self.total_grid_h), pygame.SRCALPHA)

            for i, card in enumerate(self.cards):
                row = i // self.max_cols
                col = i % self.max_cols
                card_x = self.grid_start_x + col * (CARD_W + self.grid_padding_x)
                card_y = row * (CARD_H + self.grid_padding_y)
                card.draw(game_canvas, card_x, card_y)

            screen.blit(game_canvas, (0, self.grid_start_y),
                        (0, self.scroll_y, WIDTH, HEIGHT - self.grid_start_y - 40))

            header_rect = pygame.Rect(30, 15, WIDTH - 60, 60)
            pygame.draw.rect(screen, COLOUR_HEADER_BG, header_rect, border_radius=6)
            pygame.draw.rect(screen, COLOUR_HEADER_BORDER, header_rect, 2, border_radius=6)

            if self.selected_style == "Single Player":
                ui_str = (f"Mode: {self.selected_diff}   |   Pairs Found: {self.p1_pairs}/{self.num_pairs}"
                          f"   |   Lives: {self.lives}")
            else:
                p2_lbl = "AI" if self.selected_style == "AI VS" else "Player 2"
                turn_lbl = "Player 1" if self.current_turn == 1 else p2_lbl
                ui_str = (f"Turn: {turn_lbl}   |   P1 Pairs: {self.p1_pairs}   |   {p2_lbl} Pairs: {self.p2_pairs}"
                          f" (Max: {self.num_pairs})")

            ui_surf = font_header.render(ui_str, True, COLOUR_TEXT_LIGHT)
            screen.blit(ui_surf, ui_surf.get_rect(center=header_rect.center))

            scroll_lbl = font_ui.render("* Use Mouse Wheel to scroll cards if needed *", True, COLOUR_TEXT_LIGHT)
            screen.blit(scroll_lbl, scroll_lbl.get_rect(center=(WIDTH//2, HEIGHT - 10)))

            if self.state == "GAME_OVER":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))

                box = pygame.Rect(250, 280, 500, 180)
                pygame.draw.rect(screen, COLOUR_MENU_BG, box, border_radius=6)
                pygame.draw.rect(screen, COLOUR_CARD_BORDER, box, 3, border_radius=6)

                go_surf = font_title.render("ROUND OVER", True, COLOUR_RED)
                msg_surf = font_header.render(self.game_over_msg, True, COLOUR_WHITE)
                sub_surf = font_ui.render("Click anywhere to return to main menu", True, COLOUR_TEXT_LIGHT)

                screen.blit(go_surf, go_surf.get_rect(center=(WIDTH//2, box.top + 25)))
                screen.blit(msg_surf, msg_surf.get_rect(center=(WIDTH//2, box.top + 80)))
                screen.blit(sub_surf, sub_surf.get_rect(center=(WIDTH//2, box.top + 130)))

# --- MAIN LOOP ---
manager = GameManager()
while True:
    manager.process_events()
    manager.update()
    manager.draw(screen)
    pygame.display.flip()
    clock.tick(60)
