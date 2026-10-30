# ======[ D I F F I C U L T Y   S E L E C T ]======
# generic difficulty selection screen - shows up right after mode select,
# same pattern as mode_select.py: reads a DIFFICULTIES dict and builds
# a button per entry. No manual per-game menu building needed.
#
# Lives in src/{game}/difficulties/ instead of src/{game}/ itself, e.g.
# Pong's is src/games/pong/difficulties/, with diff_1.py, diff_2.py,
# diff_3.py inside and an __init__.py exporting DIFFICULTIES = {label:
# module_name}. Every diff_N.py just names its class "Difficulty" so
# this screen doesn't have to scan/guess which class to load.

import pygame
import importlib
from src.core.constants import *

class DifficultySelectScreen:
    """
    Shown after ModeSelectScreen, if (and only if) the chosen game has a
    difficulties/ package. Builds buttons from a DIFFICULTIES dict the
    exact same way ModeSelectScreen builds buttons from a MODES dict.
    """

    def __init__(self, game_display_name, game_module_prefix, difficulties_dict):
        """
        game_display_name  - "Pong", "Breakout" etc.
        game_module_prefix - "src.games.pong"
        difficulties_dict  - {"Classic": "diff_1", "Advanced": "diff_2", ...}
        """
        self.display_name = game_display_name
        self.module_prefix = game_module_prefix
        self.difficulties = difficulties_dict  # {label: diff_module_name}
        self.selected_label = None
        self.done = False
        self.next_state = None  # will hold the instantiated Difficulty object
        
        self.font_title = title_font()
        self.font_body = body_font()
        self.font_small = make_font(16)

        # pre-load each difficulty's blurb once instead of importing on
        # every single draw() call
        self.descriptions = {}
        for label, mod_name in difficulties_dict.items():
            full_path = f"{game_module_prefix}.difficulties.{mod_name}"
            try:
                mod = importlib.import_module(full_path)
                diff_cls = getattr(mod, "Difficulty", None)
                self.descriptions[label] = getattr(diff_cls, "description", "") if diff_cls else ""
            except Exception as e:
                print(f"  [DifficultySelect] Couldn't pre-load {full_path}: {e}")
                self.descriptions[label] = ""

        # build button rects - stacked vertically in the centre, same
        # layout math as ModeSelectScreen
        self.buttons = []
        btn_w, btn_h = scale_size(300), scale_y(55)
        gap = scale_y(15)
        total_h = len(difficulties_dict) * (btn_h + gap) - gap
        start_y = (SCREEN_HEIGHT - total_h) // 2

        for i, label in enumerate(difficulties_dict.keys()):
            x = (SCREEN_WIDTH - btn_w) // 2
            y = start_y + i * (btn_h + gap)
            self.buttons.append({
                "label": label,
                "rect": pygame.Rect(x, y, btn_w, btn_h),
            })

    def load_selected_difficulty(self):
        """
        Import diff_module_name from {module_prefix}.difficulties, grab
        its "Difficulty" class, instantiate and return it.
        """
        diff_mod_name = self.difficulties[self.selected_label]
        full_path = f"{self.module_prefix}.difficulties.{diff_mod_name}"
        try:
            mod = importlib.import_module(full_path)
            diff_cls = getattr(mod, "Difficulty", None)
            if diff_cls:
                return diff_cls()
            print(f"  [DifficultySelect] No Difficulty class found in {full_path}")
            return None
        except Exception as e:
            print(f"  [DifficultySelect] Error loading {full_path}: {e}")
            return None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.done = True
                self.next_state = None      # carousel treats this as "cancel"
                return
            elif event.key in (pygame.K_RETURN, pygame.K_e) and self.selected_label:
                diff_obj = self.load_selected_difficulty()
                if diff_obj:
                    self.next_state = diff_obj
                    self.done = True
                return
            elif event.key == pygame.K_UP:
                labels = list(self.difficulties.keys())
                idx = labels.index(self.selected_label) if self.selected_label in labels else 0
                self.selected_label = labels[(idx - 1) % len(labels)]
            elif event.key == pygame.K_DOWN:
                labels = list(self.difficulties.keys())
                idx = labels.index(self.selected_label) if self.selected_label in labels else -1
                self.selected_label = labels[(idx + 1) % len(labels)]

        # mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn["rect"].collidepoint(event.pos):
                    self.selected_label = btn["label"]
                    diff_obj = self.load_selected_difficulty()
                    if diff_obj:
                        self.next_state = diff_obj
                        self.done = True
                    return

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(COL_BG)

        # title
        title = self.font_title.render(f"{self.display_name} - Difficulty", True, COL_YELLOW)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, scale_y(120)))

        # subtitle
        sub = self.font_body.render("Select a difficulty", True, COL_TEXT_MUTED)
        surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, scale_y(170)))

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

        # blurb for whichever difficulty is currently highlighted
        if self.selected_label:
            desc_text = self.descriptions.get(self.selected_label, "")
            if desc_text:
                desc_surf = self.font_small.render(desc_text, True, COL_TEXT_MUTED)
                surface.blit(desc_surf, (SCREEN_WIDTH // 2 - desc_surf.get_width() // 2,
                                          self.buttons[-1]["rect"].bottom + scale_y(25)))

        # bottom text
        hint = self.font_body.render(r"/\ \/ to navigate   ENTER to select   ESC to go back", True, COL_TEXT_MUTED)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - scale_y(40)))

    def cleanup(self):
        pass
