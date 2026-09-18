# ======[ M O D E   S E L E C T ]======
# generic mode selection screen
# reads a game's MODES dict and draws buttons for each mode
# no more manual menu-building for every new game

import pygame
import importlib
from src.core.constants import *

class ModeSelectScreen:
    """
    When a game has multiple modes (e.g. "1 Player", "2 Players",
    "AI Versus") this screen appears and builds buttons automatically.
    No manual rect creation per game - just define MODES in __init__.py.
    """

    def __init__(self, game_display_name, game_module_prefix, modes_dict):
        """
        game_display_name - "Breakout", "Tetris" etc.
        game_module_prefix - "src.games.breakout"
        modes_dict - {"1 Player": "mode_1p", "2 Players": "mode_2p", ...}
        """
        self.display_name = game_display_name
        self.module_prefix = game_module_prefix
        self.modes = modes_dict # {label: mode_module_name}
        self.selected_label = None
        self.done = False
        self.next_state = None # will hold the instantiated mode object

        self.font_title = pygame.font.Font(None, FONT_TITLE_SIZE)
        self.font_body = pygame.font.Font(None, FONT_BODY_SIZE)

        # build button rects - stacked vertically in the centre
        self.buttons = []
        btn_w, btn_h = 300, 55
        gap = 15
        total_h = len(modes_dict) * (btn_h + gap) - gap
        start_y = (SCREEN_HEIGHT - total_h) // 2

        for i, label in enumerate(modes_dict.keys()):
            x = (SCREEN_WIDTH - btn_w) // 2
            y = start_y + i * (btn_h + gap)
            self.buttons.append({
                "label": label,
                "rect": pygame.Rect(x, y, btn_w, btn_h),
            })

    def launch_selected_mode(self):
        """
        Import mode_module_name from the game package, instantiate it, return it.
        e.g. "src.games.breakout.mode_1p" → class instance
        """
        mode_mod_name = self.modes[self.selected_label]
        full_path = f"{self.module_prefix}.{mode_mod_name}"
        try:
            mod = importlib.import_module(full_path)
            # prefer classes actually defined in this module (not imported from elsewhere)
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if isinstance(attr, type) and attr.__module__ == full_path and attr_name.endswith("Mode"):
                    return attr()
            # fallback: any class ending in "Mode" (may include imported base classes)
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if isinstance(attr, type) and attr_name.endswith("Mode"):
                    return attr()
            print(f"  [ModeSelect] No mode class found in {full_path}")
            return None
        except Exception as e:
            print(f"  [ModeSelect] Error loading {full_path}: {e}")
            return None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.done = True
                self.next_state = None      # go back to carousel
            elif event.key in (pygame.K_RETURN, pygame.K_e) and self.selected_label:
                mode_obj = self.launch_selected_mode()
                if mode_obj:
                    self.next_state = mode_obj
                    self.done = True
                return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                labels = list(self.modes.keys())
                idx = labels.index(self.selected_label) if self.selected_label in labels else 0
                self.selected_label = labels[(idx - 1) % len(labels)]
            elif event.key == pygame.K_DOWN:
                labels = list(self.modes.keys())
                idx = labels.index(self.selected_label) if self.selected_label in labels else -1
                self.selected_label = labels[(idx + 1) % len(labels)]

        # mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn["rect"].collidepoint(event.pos):
                    self.selected_label = btn["label"]
                    mode_obj = self.launch_selected_mode()
                    if mode_obj:
                        self.next_state = mode_obj
                        self.done = True
                    return

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(COL_BG)

        # title
        title = self.font_title.render(self.display_name, True, COL_YELLOW)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 120))

        # subtitle
        sub = self.font_body.render("Select a mode", True, COL_TEXT_MUTED)
        surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 170))

        # buttons
        for btn in self.buttons:
            selected = (btn["label"] == self.selected_label)
            colour = COL_DARK_RED if selected else COL_CARD_BORDER
            pygame.draw.rect(surface, colour, btn["rect"], border_radius=6)
            if not selected:
                pygame.draw.rect(surface, COL_CARD_BORDER, btn["rect"], 2, border_radius=6)

            label_surf = self.font_body.render(btn["label"], True, COL_TEXT)
            surface.blit(label_surf,
                (btn["rect"].centerx - label_surf.get_width() // 2,
                 btn["rect"].centery - label_surf.get_height() // 2))

        # hint at the bottom
        hint = self.font_body.render(r"/\ \/ to navigate   E N T E R to select   E S C to go back", True, COL_TEXT_MUTED)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40))

    def cleanup(self):
        pass