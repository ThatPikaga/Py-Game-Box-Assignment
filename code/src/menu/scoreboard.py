# scoreboard.py — Overlay that shows saved results for the selected game
# Press T on the carousel to open it; ESC or Back closes it
# It uses the same overlay approach as Settings, so the carousel stays underneath.

import pygame
import json
import os

from src.core.constants import *
from src.core.stats import stats_file_path

class Scoreboard:
    def __init__(self):
        self.name = "SCOREBOARD"
        self.done = False
        self.next_state = None
        self.persist = {}
        self.font_title = None
        self.font_body = None
        self.font_small = None
        
        # Current game context (which game's stats to show)
        self.game_name = ""
        self.stats_data = []
        
        # UI elements
        self.back_btn = None
    
    def _get_stats_file(self, game_name):
        """Use the same automatic filename rule as the save helper."""
        code_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        return stats_file_path(code_dir, game_name)
    
    def _load_stats(self, game_name):
        """Load stats from JSON file for the given game."""
        stats_file = self._get_stats_file(game_name)
        
        try:
            with open(stats_file, 'r') as f:
                data = json.load(f)
                # Convert dict to list of entries for display
                entries = []
                for username, stats in data.items():
                    if isinstance(stats, dict):
                        # Old save files only have 'score'; newer games can name another metric.
                        metric_label = stats.get("metric_label")
                        metric_value = stats.get("best_metric_value")
                        if metric_value is None:
                            metric_value = stats.get("best_score", stats.get("score"))
                        if metric_label is None and metric_value is not None:
                            metric_label = "Score"
                        entries.append({
                            "username": username,
                            "score": metric_value,
                            "metric_label": metric_label,
                            "games_played": stats.get("games_played", 1),
                        })

                # Players with a number are ranked first; if there is no number,
                # showing the most active players is still useful.
                entries.sort(key=lambda item: (
                    item["score"] is not None,
                    item["score"] if item["score"] is not None else item["games_played"],
                ), reverse=True)
                return entries[:10]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def startup(self, persist):
        self.persist = persist
        self.done = False
        self.font_title = title_font()
        self.font_body = body_font()
        self.font_small = header_font()
        
        # Get game context from persist
        self.game_name = persist.get("scoreboard_context", persist.get("settings_context", "Unknown"))
        
        # Load stats for this game
        self.stats_data = self._load_stats(self.game_name)
        
        # Initialize UI
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT
        self.back_btn = pygame.Rect(scale_x(20), h - scale_y(80), scale_x(100), scale_y(40))
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.done = True
                self.next_state = "MAIN_MENU"
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                if self.back_btn.collidepoint(mouse_pos):
                    self.done = True
                    self.next_state = "MAIN_MENU"
    
    def update(self, dt):
        pass
    
    def draw(self, surface):
        w, h = surface.get_size()

        # Copy the Settings overlay idea: dim the screen, then draw the scoreboard panel.
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        surface.blit(overlay, (0, 0))

        panel = pygame.Rect(scale_x(60), scale_y(35), w - scale_x(120), h - scale_y(70))
        pygame.draw.rect(surface, COL_BG, panel, border_radius=10)
        pygame.draw.rect(surface, COL_CARD_BORDER, panel, 2, border_radius=10)

        # Draw the title with the currently selected game's name.
        title = self.font_title.render(f"{self.game_name} - SCOREBOARD", True, COL_GOLD)
        surface.blit(title, (w // 2 - title.get_width() // 2, panel.top + scale_y(20)))

        # Each game can show its own metric label, such as Score or Wave.
        metric_label = next((entry.get("metric_label") for entry in self.stats_data
                             if entry.get("metric_label")), "Metric")
        headers = ["Rank", "Username", metric_label, "Games Played"]
        col_widths = [scale_x(60), scale_x(200), scale_x(150), scale_x(150)]
        x_offset = (w - sum(col_widths)) // 2
        header_y = panel.top + scale_y(90)

        for i, header in enumerate(headers):
            header_surface = self.font_body.render(header, True, COL_TEXT_MUTED)
            surface.blit(header_surface, (x_offset + sum(col_widths[:i]) + scale_x(10), header_y))

        line_y = header_y + scale_y(40)
        pygame.draw.line(surface, COL_CARD_BORDER, (panel.left + scale_x(20), line_y),
                         (panel.right - scale_x(20), line_y), 2)

        if not self.stats_data:
            no_data = self.font_body.render(
                "No stats recorded yet - play a game to populate", True, COL_TEXT_MUTED
            )
            surface.blit(no_data, (w // 2 - no_data.get_width() // 2, line_y + scale_y(80)))
        else:
            for i, entry in enumerate(self.stats_data):
                row_y = line_y + scale_y(20) + i * scale_y(45)

                rank_color = COL_GOLD if i < 3 else COL_TEXT
                rank_surface = self.font_body.render(f"#{i + 1}", True, rank_color)
                surface.blit(rank_surface, (x_offset + scale_x(10), row_y))

                username_surface = self.font_body.render(entry["username"], True, COL_TEXT)
                surface.blit(username_surface, (x_offset + col_widths[0] + scale_x(10), row_y))

                metric_value = "—" if entry["score"] is None else str(entry["score"])
                metric_color = COL_LIME if i == 0 and entry["score"] is not None else COL_TEXT
                metric_surface = self.font_body.render(metric_value, True, metric_color)
                surface.blit(metric_surface, (x_offset + col_widths[0] + col_widths[1] + scale_x(10), row_y))

                games_surface = self.font_body.render(str(entry["games_played"]), True, COL_TEXT)
                surface.blit(games_surface, (
                    x_offset + col_widths[0] + col_widths[1] + col_widths[2] + scale_x(10), row_y
                ))

        # The Back button and Escape key both close the overlay.
        pygame.draw.rect(surface, COL_DARK_RED, self.back_btn, border_radius=5)
        back_txt = self.font_body.render("Back", True, COL_WHITE)
        surface.blit(back_txt, (
            self.back_btn.centerx - back_txt.get_width() // 2,
            self.back_btn.centery - back_txt.get_height() // 2,
        ))

        instructions = self.font_small.render(
            "Press ESC or click Back to return", True, COL_TEXT_MUTED
        )
        surface.blit(instructions, (w // 2 - instructions.get_width() // 2, h - scale_y(40)))
    
    def cleanup(self):
        pass
