# scoreboard.py — Scoreboard screen that shows saved stats per game
# Press T on the carousel to view stats; ESC to return
# Loads from data/*_stats.json files and displays usernames with scores

import pygame
import json
import os

from src.core.constants import *

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
        """Get the stats file path for a given game."""
        game_key = game_name.replace(" ", "_").lower()
        return os.path.join(os.path.dirname(__file__), "..", "..", "data", f"{game_key}_stats.json")
    
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
                        # Extract score - different games may have different fields
                        score = stats.get("score", stats.get("high_score", stats.get("wins", 0)))
                        games_played = stats.get("games_played", 1)
                        entries.append({
                            "username": username,
                            "score": score,
                            "games_played": games_played,
                        })
                
                # Sort by score descending
                entries.sort(key=lambda x: x["score"], reverse=True)
                return entries[:10]  # Top 10
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
        self.back_btn = pygame.Rect(20, h - 80, 100, 40)
    
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
        surface.fill(COL_BG)
        
        w, h = surface.get_size()
        
        # Draw title with game name
        title = self.font_title.render(f"{self.game_name} - SCOREBOARD", True, COL_GOLD)
        surface.blit(title, (w // 2 - title.get_width() // 2, 30))
        
        # Draw column headers
        header_font = self.font_body
        headers = ["Rank", "Username", "Score", "Games Played"]
        col_widths = [60, 200, 150, 150]
        x_offset = 100
        
        for i, header in enumerate(headers):
            txt = header_font.render(header, True, COL_TEXT_MUTED)
            surface.blit(txt, (x_offset + sum(col_widths[:i]) + 10, 90))
        
        # Draw separator line
        pygame.draw.line(surface, COL_CARD_BORDER, (80, 130), (w - 80, 130), 2)
        
        # Draw stats entries
        if not self.stats_data:
            no_data = self.font_body.render("No stats recorded yet - play a game to populate", True, COL_TEXT_MUTED)
            surface.blit(no_data, (w // 2 - no_data.get_width() // 2, 250))
        else:
            for i, entry in enumerate(self.stats_data):
                y = 150 + i * 45
                
                # Rank
                rank_txt = self.font_body.render(f"#{i+1}", True, COL_GOLD if i < 3 else COL_TEXT)
                surface.blit(rank_txt, (x_offset + 10, y))
                
                # Username
                user_txt = self.font_body.render(entry["username"], True, COL_TEXT)
                surface.blit(user_txt, (x_offset + col_widths[0] + 10, y))
                
                # Score
                score_txt = self.font_body.render(str(entry["score"]), True, COL_LIME if i == 0 else COL_TEXT)
                surface.blit(score_txt, (x_offset + col_widths[0] + col_widths[1] + 10, y))
                
                # Games Played
                games_txt = self.font_body.render(str(entry["games_played"]), True, COL_TEXT)
                surface.blit(games_txt, (x_offset + col_widths[0] + col_widths[1] + col_widths[2] + 10, y))
        
        # Draw Back button
        pygame.draw.rect(surface, COL_DARK_RED, self.back_btn, border_radius=5)
        back_txt = self.font_body.render("Back", True, COL_WHITE)
        surface.blit(back_txt, (self.back_btn.centerx - back_txt.get_width() // 2,
                                 self.back_btn.centery - back_txt.get_height() // 2))
        
        # Draw instructions
        instr = self.font_small.render("Press ESC or click Back to return", True, COL_TEXT_MUTED)
        surface.blit(instr, (w // 2 - instr.get_width() // 2, h - 40))
    
    def cleanup(self):
        pass
