Absolutely — the code got mangled in several places near update(), evaluate_match(), draw(), and the runtime loop. I’ve reformatted it and repaired the obvious syntax/formatting corruption while keeping the intended game logic.

import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# --- WINDOW CONFIGURATION ---
WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Match")
clock = pygame.time.Clock()

# --- COLORS ---
COLOR_WOOD_DARK = (74, 46, 27)
COLOR_WOOD_LIGHT = (92, 58, 35)
COLOR_WOOD_GRAIN = (66, 41, 22)
COLOR_MENU_BG = (45, 26, 15)
COLOR_TEXT_LIGHT = (240, 210, 180)
COLOR_WHITE = (255, 255, 255)
COLOR_CARD_FRONT = (251, 246, 235)
COLOR_CARD_BORDER = (212, 175, 55)
COLOR_CARD_TEXT = (26, 26, 26)
COLOR_RED_CHEQUER = (178, 34, 34)
COLOR_WHITE_CHEQUER = (240, 240, 240)
COLOR_MATCHED = (128, 128, 128)
COLOR_HEADER_BG = (54, 34, 17)

# --- FONTS ---
font_title = pygame.font.SysFont("helvetica", 36, bold=True)
font_header = pygame.font.SysFont("helvetica", 20, bold=True)
font_ui = pygame.font.SysFont("helvetica", 16, bold=True)
font_card = pygame.font.SysFont("helvetica", 22, bold=True)


# --- PROCEDURAL ASSETS ---
def draw_wood_floor(surface):
    """Draw a generic wood plank floor background."""
    surface.fill(COLOR_WOOD_DARK)

    plank_h = 40
    plank_w = 120

    for y in range(0, HEIGHT, plank_h):
        offset = (y // plank_h % 2) * (plank_w // 2)

        for x in range(-plank_w, WIDTH + plank_w, plank_w):
            px = x + offset

            color = (
                COLOR_WOOD_LIGHT
                if (x // plank_w + y // plank_h) % 2 == 0
                else COLOR_WOOD_DARK
            )

            pygame.draw.rect(
                surface,
                color,
                (px, y, plank_w, plank_h),
            )

            pygame.draw.rect(
                surface,
                COLOR_WOOD_GRAIN,
                (px, y, plank_w, plank_h),
                1,
            )

            # Grain accents
            pygame.draw.line(
                surface,
                COLOR_WOOD_GRAIN,
                (px + 10, y + 15),
                (px + plank_w - 10, y + 15),
                1,
            )

            pygame.draw.line(
                surface,
                COLOR_WOOD_GRAIN,
                (px + 20, y + 28),
                (px + plank_w - 30, y + 28),
                1,
            )


# Pre-render background for performance optimization
BACKGROUND_SURFACE = pygame.Surface((WIDTH, HEIGHT))
draw_wood_floor(BACKGROUND_SURFACE)


def get_card_back_surface(w, h):
    """Generate a reusable surface with a red-and-white chequered pattern."""
    surf = pygame.Surface((w, h))
    surf.fill(COLOR_WHITE_CHEQUER)

    sz = 8

    for y in range(0, h, sz):
        for x in range(0, w, sz):
            if (x // sz + y // sz) % 2 == 0:
                pygame.draw.rect(
                    surf,
                    COLOR_RED_CHEQUER,
                    (x, y, sz, sz),
                )

    return surf


CARD_W, CARD_H = 55, 75
CARD_BACK_SURF = get_card_back_surface(CARD_W, CARD_H)


# --- GAME ENGINE STATE CLASSES ---
class MenuButton:
    def __init__(self, text, x, y, w, h, var_type, value):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.var_type = var_type  # "style", "diff", or "start"
        self.value = value

    def draw(self, screen, current_selection):
        is_selected = current_selection == self.value

        bg_color = (
            (139, 90, 43)
            if (is_selected or self.var_type == "start")
            else (30, 15, 8)
        )

        border_color = (
            COLOR_CARD_BORDER
            if is_selected
            else (80, 50, 30)
        )

        pygame.draw.rect(
            screen,
            bg_color,
            self.rect,
            border_radius=4,
        )

        pygame.draw.rect(
            screen,
            border_color,
            self.rect,
            2,
            border_radius=4,
        )

        txt_surf = font_ui.render(
            self.text,
            True,
            COLOR_WHITE,
        )

        txt_rect = txt_surf.get_rect(
            center=self.rect.center
        )

        screen.blit(txt_surf, txt_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Card:
    def __init__(self, value, index):
        self.value = value
        self.index = index
        self.is_flipped = False
        self.is_matched = False
        self.rect = pygame.Rect(
            0,
            0,
            CARD_W,
            CARD_H,
        )

    def draw(self, surface, x, y):
        self.rect.topleft = (x, y)

        if self.is_matched:
            pygame.draw.rect(
                surface,
                COLOR_MATCHED,
                self.rect,
                border_radius=3,
            )

            pygame.draw.rect(
                surface,
                (60, 60, 60),
                self.rect,
                1,
                border_radius=3,
            )

        elif self.is_flipped:
            pygame.draw.rect(
                surface,
                COLOR_CARD_FRONT,
                self.rect,
                border_radius=3,
            )

            pygame.draw.rect(
                surface,
                COLOR_CARD_BORDER,
                self.rect,
                2,
                border_radius=3,
            )

            val_surf = font_card.render(
                str(self.value),
                True,
                COLOR_CARD_TEXT,
            )

            val_rect = val_surf.get_rect(
                center=self.rect.center
            )

            surface.blit(val_surf, val_rect)

        else:
            surface.blit(
                CARD_BACK_SURF,
                (x, y),
            )

            pygame.draw.rect(
                surface,
                (34, 17, 5),
                self.rect,
                1,
                border_radius=3,
            )


class GameManager:
    def __init__(self):
        self.state = "MENU"
        self.selected_style = "Single Player"
        self.selected_diff = "Easy"

        self.init_menu_ui()

    def init_menu_ui(self):
        self.menu_buttons = [
            # Playstyles
            MenuButton(
                "Single Player",
                320,
                220,
                160,
                40,
                "style",
                "Single Player",
            ),
            MenuButton(
                "Local VS",
                500,
                220,
                160,
                40,
                "style",
                "Local VS",
            ),
            MenuButton(
                "AI VS",
                410,
                270,
                160,
                40,
                "style",
                "AI VS",
            ),

            # Difficulties
            MenuButton(
                "Easy (24)",
                230,
                410,
                160,
                40,
                "diff",
                "Easy",
            ),
            MenuButton(
                "Medium (52)",
                410,
                410,
                160,
                40,
                "diff",
                "Medium",
            ),
            MenuButton(
                "Hard (104)",
                590,
                410,
                160,
                40,
                "diff",
                "Hard",
            ),

            # Start Action
            MenuButton(
                "START GAME",
                400,
                560,
                180,
                50,
                "start",
                "START",
            ),
        ]

    def init_game_board(self):
        diff_config = {
            "Easy": {
                "pairs": 12,
                "lives": 18,
                "cols": 6,
            },
            "Medium": {
                "pairs": 26,
                "lives": 31,
                "cols": 13,
            },
            "Hard": {
                "pairs": 52,
                "lives": 52,
                "cols": 13,
            },
        }

        config = diff_config[self.selected_diff]

        self.num_pairs = config["pairs"]
        self.lives = config["lives"]
        self.max_cols = config["cols"]

        # Scoring systems
        self.p1_pairs = 0
        self.p2_pairs = 0
        self.current_turn = 1  # 1 = P1, 2 = P2/AI

        # Card generation
        values = list(range(1, self.num_pairs + 1)) * 2
        random.shuffle(values)

        self.cards = [
            Card(val, i)
            for i, val in enumerate(values)
        ]

        # Grid coordinate calculation
        self.grid_padding_x = 12
        self.grid_padding_y = 12

        self.total_grid_w = (
            self.max_cols * (CARD_W + self.grid_padding_x)
            - self.grid_padding_x
        )

        self.grid_start_x = (
            WIDTH - self.total_grid_w
        ) // 2

        self.grid_start_y = 100

        # Vertical scrolling system
        self.scroll_y = 0

        total_rows = (
            len(self.cards) + self.max_cols - 1
        ) // self.max_cols

        self.total_grid_h = (
            total_rows * (CARD_H + self.grid_padding_y)
            + 50
        )

        self.max_scroll = max(
            0,
            (
                self.grid_start_y
                + self.total_grid_h
            )
            - (HEIGHT - 40),
        )

        # Action management variables
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
                    # Left click
                    self.handle_click(event.pos)

                elif (
                    event.button == 4
                    and self.state == "PLAYING"
                ):
                    # Scroll up
                    self.scroll_y = max(
                        0,
                        self.scroll_y - 30,
                    )

                elif (
                    event.button == 5
                    and self.state == "PLAYING"
                ):
                    # Scroll down
                    self.scroll_y = min(
                        self.max_scroll,
                        self.scroll_y + 30,
                    )

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
            # Clicking anywhere returns to config screen
            self.state = "MENU"
            return

        if (
            self.state == "PLAYING"
            and not self.lock_board
        ):
            # Block human interaction during AI turn
            if (
                self.selected_style == "AI VS"
                and self.current_turn == 2
            ):
                return

            adjusted_pos = (
                pos[0],
                pos[1] + self.scroll_y,
            )

            for card in self.cards:
                if (
                    card.rect.collidepoint(adjusted_pos)
                    and not card.is_flipped
                    and not card.is_matched
                ):
                    self.flip_card(card.index)
                    break

    def flip_card(self, idx):
        self.cards[idx].is_flipped = True
        self.selected_indices.append(idx)

        if len(self.selected_indices) == 2:
            self.lock_board = True
            self.cooldown_timer = (
                pygame.time.get_ticks() + 800
            )

    def update(self):
        if self.state != "PLAYING":
            return

        current_time = pygame.time.get_ticks()

        # Resolve card match after the delay
        if (
            self.lock_board
            and self.cooldown_timer > 0
            and current_time >= self.cooldown_timer
        ):
            self.evaluate_match()
            self.cooldown_timer = 0

            # Check game over
            if all(c.is_matched for c in self.cards):
                self.trigger_game_over(
                    all_cleared=True
                )

            elif (
                self.selected_style == "Single Player"
                and self.lives <= 0
            ):
                self.trigger_game_over(
                    all_cleared=False
                )

            else:
                # Start AI turn after a short delay
                if (
                    self.selected_style == "AI VS"
                    and self.current_turn == 2
                    and not self.lock_board
                ):
                    self.ai_timer = (
                        current_time + 600
                    )

        # Execute AI turn
        if (
            self.selected_style == "AI VS"
            and self.current_turn == 2
            and not self.lock_board
            and self.ai_timer > 0
            and current_time >= self.ai_timer
        ):
            self.execute_ai_turn()
            self.ai_timer = 0

    def evaluate_match(self):
        idx1, idx2 = self.selected_indices

        c1 = self.cards[idx1]
        c2 = self.cards[idx2]

        if c1.value == c2.value:
            c1.is_matched = True
            c2.is_matched = True

            if self.current_turn == 1:
                self.p1_pairs += 1
            else:
                self.p2_pairs += 1

        else:
            c1.is_flipped = False
            c2.is_flipped = False

            if self.selected_style == "Single Player":
                self.lives -= 1
            else:
                self.current_turn = (
                    2
                    if self.current_turn == 1
                    else 1
                )

        self.selected_indices.clear()
        self.lock_board = False

    def execute_ai_turn(self):
        available = [
            c.index
            for c in self.cards
            if not c.is_flipped and not c.is_matched
        ]

        if len(available) >= 2:
            choices = random.sample(
                available,
                2,
            )

            self.flip_card(choices[0])
            self.flip_card(choices[1])

    def trigger_game_over(self, all_cleared):
        self.state = "GAME_OVER"

        if self.selected_style == "Single Player":
            if all_cleared:
                self.game_over_msg = (
                    f"Game Over! Found all pairs "
                    f"with {self.lives} lives remaining!"
                )
            else:
                self.game_over_msg = (
                    "Game Over! Out of lives!"
                )

        else:
            p2_lbl = (
                "AI"
                if self.selected_style == "AI VS"
                else "Player 2"
            )

            if self.p1_pairs > self.p2_pairs:
                self.game_over_msg = (
                    f"Player 1 wins with "
                    f"{self.p1_pairs} pairs!"
                )

            elif self.p2_pairs > self.p1_pairs:
                self.game_over_msg = (
                    f"{p2_lbl} wins with "
                    f"{self.p2_pairs} pairs!"
                )

            else:
                self.game_over_msg = (
                    f"It's a tie! Both secured "
                    f"{self.p1_pairs} pairs."
                )

    def draw(self, screen):
        # Always draw background
        screen.blit(
            BACKGROUND_SURFACE,
            (0, 0),
        )

        if self.state == "MENU":
            # Frame box
            menu_rect = pygame.Rect(
                200,
                100,
                600,
                550,
            )

            pygame.draw.rect(
                screen,
                COLOR_MENU_BG,
                menu_rect,
                border_radius=8,
            )

            pygame.draw.rect(
                screen,
                COLOR_CARD_BORDER,
                menu_rect,
                3,
                border_radius=8,
            )

            # Title
            title_surf = font_title.render(
                "MEMORY MATCH",
                True,
                COLOR_TEXT_LIGHT,
            )

            screen.blit(
                title_surf,
                title_surf.get_rect(
                    centerx=WIDTH // 2,
                    top=130,
                ),
            )

            # Playstyle label
            lbl_style = font_header.render(
                "Select Playstyle:",
                True,
                COLOR_WHITE,
            )

            screen.blit(
                lbl_style,
                lbl_style.get_rect(
                    centerx=WIDTH // 2,
                    top=185,
                ),
            )

            # Difficulty label
            lbl_diff = font_header.render(
                "Select Difficulty:",
                True,
                COLOR_WHITE,
            )

            screen.blit(
                lbl_diff,
                lbl_diff.get_rect(
                    centerx=WIDTH // 2,
                    top=370,
                ),
            )

            # Menu buttons
            for btn in self.menu_buttons:
                if btn.var_type == "style":
                    current_selection = self.selected_style
                elif btn.var_type == "diff":
                    current_selection = self.selected_diff
                else:
                    current_selection = None

                btn.draw(
                    screen,
                    current_selection,
                )

        elif self.state in ["PLAYING", "GAME_OVER"]:
            # Create scrolling game canvas
            game_canvas = pygame.Surface(
                (WIDTH, self.total_grid_h),
                pygame.SRCALPHA,
            )

            # Draw cards
            for i, card in enumerate(self.cards):
                row = i // self.max_cols
                col = i % self.max_cols

                card_x = (
                    self.grid_start_x
                    + col
                    * (
                        CARD_W
                        + self.grid_padding_x
                    )
                )

                card_y = (
                    row
                    * (
                        CARD_H
                        + self.grid_padding_y
                    )
                )

                card.draw(
                    game_canvas,
                    card_x,
                    card_y,
                )

            # Blit visible portion of scrolling canvas
            screen.blit(
                game_canvas,
                (0, self.grid_start_y),
                (
                    0,
                    self.scroll_y,
                    WIDTH,
                    HEIGHT
                    - self.grid_start_y
                    - 40,
                ),
            )

            # Header
            header_rect = pygame.Rect(
                30,
                15,
                WIDTH - 60,
                60,
            )

            pygame.draw.rect(
                screen,
                COLOR_HEADER_BG,
                header_rect,
                border_radius=6,
            )

            pygame.draw.rect(
                screen,
                COLOR_CARD_BORDER,
                header_rect,
                2,
                border_radius=6,
            )

            if self.selected_style == "Single Player":
                ui_str = (
                    f"Mode: {self.selected_diff}"
                    f"   |   Pairs Found: "
                    f"{self.p1_pairs}/{self.num_pairs}"
                    f"   |   Lives: {self.lives}"
                )

            else:
                p2_lbl = (
                    "AI"
                    if self.selected_style == "AI VS"
                    else "Player 2"
                )

                turn_lbl = (
                    "Player 1"
                    if self.current_turn == 1
                    else p2_lbl
                )

                ui_str = (
                    f"Turn: {turn_lbl}"
                    f"   |   P1 Pairs: "
                    f"{self.p1_pairs}"
                    f"   |   {p2_lbl} Pairs: "
                    f"{self.p2_pairs}"
                    f" (Max: {self.num_pairs})"
                )

            ui_surf = font_header.render(
                ui_str,
                True,
                COLOR_TEXT_LIGHT,
            )

            screen.blit(
                ui_surf,
                ui_surf.get_rect(
                    center=header_rect.center
                ),
            )

            # Scroll instructions
            scroll_lbl = font_ui.render(
                "* Use Mouse Wheel to scroll cards if needed *",
                True,
                COLOR_TEXT_LIGHT,
            )

            screen.blit(
                scroll_lbl,
                scroll_lbl.get_rect(
                    centerx=WIDTH // 2,
                    bottom=HEIGHT - 10,
                ),
            )

            # Game-over overlay
            if self.state == "GAME_OVER":
                overlay = pygame.Surface(
                    (WIDTH, HEIGHT),
                    pygame.SRCALPHA,
                )

                overlay.fill(
                    (0, 0, 0, 180)
                )

                screen.blit(
                    overlay,
                    (0, 0),
                )

                box = pygame.Rect(
                    250,
                    280,
                    500,
                    180,
                )

                pygame.draw.rect(
                    screen,
                    COLOR_MENU_BG,
                    box,
                    border_radius=6,
                )

                pygame.draw.rect(
                    screen,
                    COLOR_CARD_BORDER,
                    box,
                    3,
                    border_radius=6,
                )

                go_surf = font_title.render(
                    "MATCH COMPLETE",
                    True,
                    COLOR_RED_CHEQUER,
                )

                msg_surf = font_header.render(
                    self.game_over_msg,
                    True,
                    COLOR_WHITE,
                )

                sub_surf = font_ui.render(
                    "Click anywhere to return to main menu",
                    True,
                    COLOR_TEXT_LIGHT,
                )

                screen.blit(
                    go_surf,
                    go_surf.get_rect(
                        centerx=WIDTH // 2,
                        top=box.top + 25,
                    ),
                )

                screen.blit(
                    msg_surf,
                    msg_surf.get_rect(
                        centerx=WIDTH // 2,
                        top=box.top + 80,
                    ),
                )

                screen.blit(
                    sub_surf,
                    sub_surf.get_rect(
                        centerx=WIDTH // 2,
                        top=box.top + 130,
                    ),
                )


# --- RUN RUNTIME LOOP ---
manager = GameManager()

while True:
    manager.process_events()
    manager.update()
    manager.draw(screen)

    pygame.display.flip()
    clock.tick(60)