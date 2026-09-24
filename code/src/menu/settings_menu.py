# settings_menu.py — Settings screen (General, Controls tabs)
# Press S on the carousel or pause menu to open; ENTER to save, ESC to exit
# Handles volume (SFX/Music), toggles, and key bindings per context
# Also includes "Learn more?" button that loads info from src/info/*.txt
 
import pygame
import json
import os
 
from src.core.constants import *
 
# Info file mappings for "Learn more?" feature
INFO_FILES = {
    "MAIN_MENU": "main_menu.txt",
    "Breakout": "breakout.txt",
    "Guess Number": "guess_num.txt",
    "Memory Match": "mem_guess.txt",
    "Pong": "pong.txt",
    "Scissors Paper Rock": "spr.txt",
    "Tetris": "tetris.txt",
}
 
class InfoPopup:
    """Small popup window that displays info text from src/info/*.txt files."""
    
    def __init__(self):
        self.active = False
        self.text_content = ""
        self.font_title = title_font()
        self.font_body = body_font()
        self.scroll_offset = 0
        self.max_lines_visible = 12
    
    def open(self, info_file_path):
        """Load and display the info file content."""
        try:
            with open(info_file_path, 'r') as f:
                self.text_content = f.read()
        except Exception as e:
            self.text_content = f"Error loading info file: {e}"
        self.scroll_offset = 0
        self.active = True
    
    def close(self):
        self.active = False
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                self.close()
                return True
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.key == pygame.K_DOWN:
                # Allow scrolling down if content is long
                self.scroll_offset += 1
        return False
    
    def draw(self, surface):
        if not self.active:
            return
        
        w, h = surface.get_size()
        
        # Dim background
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        surface.blit(overlay, (0, 0))
        
        # Popup box
        box_w, box_h = 600, 500
        box_x = w // 2 - box_w // 2
        box_y = h // 2 - box_h // 2
        
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(surface, COL_CARD_BG, box_rect)
        pygame.draw.rect(surface, COL_CARD_BORDER, box_rect, 3)
        
        # Title
        title = self.font_title.render("Learn More", True, COL_GOLD)
        surface.blit(title, (box_x + 20, box_y + 15))
        
        # Close hint
        close_txt = self.font_body.render("ESC/ENTER to close, UP/DOWN to scroll", True, COL_TEXT_MUTED)
        surface.blit(close_txt, (box_x + box_w - close_txt.get_width() - 20, box_y + 15))
        
        # Content text (with simple line wrapping)
        lines = []
        for paragraph in self.text_content.split('\n'):
            if not paragraph.strip():
                lines.append("")
                continue
            # Simple word wrapping
            words = paragraph.split()
            current_line = ""
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                test_surf = self.font_body.render(test_line, True, COL_TEXT)
                if test_surf.get_width() < box_w - 40:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
        
        # Draw visible lines based on scroll offset
        y_start = box_y + 60
        for i, line in enumerate(lines[self.scroll_offset:self.scroll_offset + self.max_lines_visible]):
            txt_surf = self.font_body.render(line, True, COL_TEXT)
            surface.blit(txt_surf, (box_x + 20, y_start + i * 25))
 
 
class SettingsMenu:
    def __init__(self):
        self.name = "SETTINGS"
        self.done = False
        self.next_state = None
        self.persist = {}
        self.font_title = None
        self.font_body = None
        self.font_small = None
        
        # Context tracking - settings are context-aware
        self.context = "MAIN_MENU"  # Can be "MAIN_MENU" or a game name
        self.context_module = None  # Module path for game-specific settings
        
        # Tabs: 0=General (Volume), 1=Controls
        self.current_tab = 0
        self.tabs = ["General", "Controls"]
        
        # Volume settings (loaded from settings files)
        self.sfx_volume = 0.7
        self.music_volume = 0.5
        self.sfx_enabled = True
        self.music_enabled = True
        
        # Key bindings (for Controls tab)
        self.bindings = {}
        self.selected_binding = None  # Which binding is being re-bound
        self.binding_wait_timer = 0
        
        # Settings file paths
        self.settings_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "settings")
        
        # Learn more popup
        self.info_popup = InfoPopup()
        
        # UI rects for buttons/toggles
        self.volume_sliders = {}
        self.toggle_btns = {}
        self.learn_more_btn = None
        self.tab_btns = []
        self.save_btn = None
        self.back_btn = None
    
    def _get_settings_file(self):
        """Get the settings file path for current context."""
        if self.context == "MAIN_MENU":
            return os.path.join(self.settings_dir, "main_menu.json")
        else:
            # Game-specific settings
            game_key = self.context.replace(" ", "_").lower()
            return os.path.join(self.settings_dir, f"{game_key}_settings.json")
    
    def _load_settings(self):
        """Load settings for current context from JSON file."""
        os.makedirs(self.settings_dir, exist_ok=True)
        settings_file = self._get_settings_file()
        
        default_settings = {
            "sfx_volume": 0.7,
            "music_volume": 0.5,
            "sfx_enabled": True,
            "music_enabled": True,
            "bindings": {}
        }
        
        try:
            with open(settings_file, 'r') as f:
                data = json.load(f)
                self.sfx_volume = data.get("sfx_volume", default_settings["sfx_volume"])
                self.music_volume = data.get("music_volume", default_settings["music_volume"])
                self.sfx_enabled = data.get("sfx_enabled", default_settings["sfx_enabled"])
                self.music_enabled = data.get("music_enabled", default_settings["music_enabled"])
                self.bindings = data.get("bindings", default_settings["bindings"])
        except (FileNotFoundError, json.JSONDecodeError):
            # Use defaults
            self.sfx_volume = default_settings["sfx_volume"]
            self.music_volume = default_settings["music_volume"]
            self.sfx_enabled = default_settings["sfx_enabled"]
            self.music_enabled = default_settings["music_enabled"]
            self.bindings = default_settings["bindings"]
    
    def _save_settings(self):
        """Save current settings to JSON file."""
        os.makedirs(self.settings_dir, exist_ok=True)
        settings_file = self._get_settings_file()
        
        data = {
            "sfx_volume": self.sfx_volume,
            "music_volume": self.music_volume,
            "sfx_enabled": self.sfx_enabled,
            "music_enabled": self.music_enabled,
            "bindings": self.bindings
        }
        
        with open(settings_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _apply_audio_settings(self):
        """Apply volume/enabled settings to pygame mixer."""
        if self.sfx_enabled:
            # Set global SFX volume
            pygame.mixer.set_num_channels(16)  # Ensure enough channels
        else:
            pygame.mixer.stop()
        
        if self.music_enabled and self.persist.get("assets", {}).get("music_manager"):
            music_mgr = self.persist["assets"]["music_manager"]
            music_mgr.set_volume(self.music_volume)
        elif not self.music_enabled and self.persist.get("assets", {}).get("music_manager"):
            pygame.mixer.music.set_volume(0)
    
    def startup(self, persist):
        self.persist = persist
        self.done = False
        self.next_state = None
        self.font_title = title_font()
        self.font_body = body_font()
        self.font_small = make_font(18)
        
        # Get context from persist (which state opened settings)
        self.context = persist.get("settings_context", "MAIN_MENU")
        self.context_module = persist.get("context_module", None)
        
        # Load settings for this context
        self._load_settings()
        
        # Initialize UI elements
        self._init_ui()
        
        # Apply audio settings
        self._apply_audio_settings()
    
    def _init_ui(self):
        """Initialize UI element positions."""
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT
        
        # Tab buttons
        tab_w, tab_h = 150, 40
        self.tab_btns = [
            pygame.Rect(w // 2 - tab_w - 10, 80, tab_w, tab_h),
            pygame.Rect(w // 2 + 10, 80, tab_w, tab_h),
        ]
        
        # Volume sliders (General tab)
        slider_y = 180
        self.volume_sliders = {
            "sfx": pygame.Rect(200, slider_y, 400, 20),
            "music": pygame.Rect(200, slider_y + 80, 400, 20),
        }
        
        # Toggle buttons
        self.toggle_btns = {
            "sfx": pygame.Rect(620, slider_y - 5, 80, 35),
            "music": pygame.Rect(620, slider_y + 75, 80, 35),
        }
        
        # Learn more button
        self.learn_more_btn = pygame.Rect(w - 140, h - 80, 120, 40)
        
        # Save button
        self.save_btn = pygame.Rect(w // 2 - 80, h - 80, 160, 45)
        
        # Back button
        self.back_btn = pygame.Rect(20, h - 80, 100, 40)
        
        # Binding slots (Controls tab)
        self.binding_slots = []
        if self.context != "MAIN_MENU":
            # Default bindings for games (can be customized per game)
            if self.context == "Pong":
                self.bindings.setdefault("P1 Up", pygame.K_w)
                self.bindings.setdefault("P1 Down", pygame.K_s)
                self.bindings.setdefault("P2 Up", pygame.K_UP)
                self.bindings.setdefault("P2 Down", pygame.K_DOWN)
            elif self.context == "Tetris":
                self.bindings.setdefault("Left", pygame.K_LEFT)
                self.bindings.setdefault("Right", pygame.K_RIGHT)
                self.bindings.setdefault("Rotate", pygame.K_UP)
                self.bindings.setdefault("Drop", pygame.K_SPACE)
            elif self.context == "Breakout":
                self.bindings.setdefault("Left", pygame.K_LEFT)
                self.bindings.setdefault("Right", pygame.K_RIGHT)
            elif self.context == "Scissors Paper Rock":
                self.bindings.setdefault("P1 Scissors", pygame.K_a)
                self.bindings.setdefault("P1 Paper", pygame.K_w)
                self.bindings.setdefault("P1 Rock", pygame.K_d)
                self.bindings.setdefault("P2 Scissors", pygame.K_LEFT)
                self.bindings.setdefault("P2 Paper", pygame.K_UP)
                self.bindings.setdefault("P2 Rock", pygame.K_RIGHT)
            
            # Create binding slot rects
            y_offset = 180
            for i, (action, key) in enumerate(self.bindings.items()):
                slot_rect = pygame.Rect(200, y_offset + i * 50, 400, 40)
                self.binding_slots.append((action, key, slot_rect))
    
    def handle_event(self, event):
        # Handle info popup first if active
        if self.info_popup.active:
            if self.info_popup.handle_event(event):
                return  # Popup handled it
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.done = True
                self.next_state = "MAIN_MENU"
                return
            
            # Tab switching with number keys
            if event.key == pygame.K_1:
                self.current_tab = 0
            elif event.key == pygame.K_2:
                self.current_tab = 1
            
            # Handle binding re-binding
            if self.selected_binding and self.binding_wait_timer > 0:
                # Capture the new key
                if event.key not in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    # Update the binding
                    action, _, _ = self.selected_binding
                    self.bindings[action] = event.key
                    self.selected_binding = None
                return
            
            # ENTER to save
            if event.key == pygame.K_RETURN:
                self._save_settings()
                self.done = True
                self.next_state = "MAIN_MENU"
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                
                # Check tab clicks
                for i, tab_rect in enumerate(self.tab_btns):
                    if tab_rect.collidepoint(mouse_pos):
                        self.current_tab = i
                        self._init_ui()  # Re-init UI for new tab
                        return
                
                # Check Learn more button
                if self.learn_more_btn.collidepoint(mouse_pos):
                    self._open_learn_more()
                    return
                
                # Check Save button
                if self.save_btn.collidepoint(mouse_pos):
                    self._save_settings()
                    self.done = True
                    self.next_state = "MAIN_MENU"
                    return
                
                # Check Back button
                if self.back_btn.collidepoint(mouse_pos):
                    self.done = True
                    self.next_state = "MAIN_MENU"
                    return
                
                # Check toggle buttons (General tab)
                if self.current_tab == 0:
                    for key, btn_rect in self.toggle_btns.items():
                        if btn_rect.collidepoint(mouse_pos):
                            if key == "sfx":
                                self.sfx_enabled = not self.sfx_enabled
                            elif key == "music":
                                self.music_enabled = not self.music_enabled
                            self._apply_audio_settings()
                            return
                    
                    # Check volume sliders
                    for key, slider_rect in self.volume_sliders.items():
                        if slider_rect.collidepoint(mouse_pos):
                            # Start dragging (simplified - just set volume based on click position)
                            rel_x = (mouse_pos[0] - slider_rect.x) / slider_rect.width
                            vol = max(0.0, min(1.0, rel_x))
                            if key == "sfx":
                                self.sfx_volume = vol
                            elif key == "music":
                                self.music_volume = vol
                            self._apply_audio_settings()
                            return
                
                # Check binding slots (Controls tab)
                if self.current_tab == 1:
                    for i, (action, key, slot_rect) in enumerate(self.binding_slots):
                        if slot_rect.collidepoint(mouse_pos):
                            # Start waiting for new key
                            self.selected_binding = (action, key, slot_rect)
                            self.binding_wait_timer = 300  # 5 seconds at 60 FPS
                            return
    
    def _open_learn_more(self):
        """Open the learn more popup with context-appropriate info file."""
        info_file = INFO_FILES.get(self.context, "main_menu.txt")
        info_path = os.path.join(os.path.dirname(__file__), "..", "info", info_file)
        self.info_popup.open(info_path)
    
    def update(self, dt):
        # Update binding wait timer
        if self.selected_binding:
            self.binding_wait_timer -= 1
            if self.binding_wait_timer <= 0:
                self.selected_binding = None
    
    def draw(self, surface):
        surface.fill(COL_BG)
        
        w, h = surface.get_size()
        
        # Draw title
        title = self.font_title.render("SETTINGS", True, COL_GOLD)
        surface.blit(title, (w // 2 - title.get_width() // 2, 20))
        
        # Draw context indicator
        ctx_txt = self.font_small.render(f"Context: {self.context}", True, COL_TEXT_MUTED)
        surface.blit(ctx_txt, (w - ctx_txt.get_width() - 20, 25))
        
        # Draw tabs
        for i, tab_name in enumerate(self.tabs):
            rect = self.tab_btns[i]
            color = COL_GOLD if i == self.current_tab else COL_TEXT_MUTED
            pygame.draw.rect(surface, color, rect, border_radius=5)
            pygame.draw.rect(surface, COL_CARD_BORDER, rect, 2, border_radius=5)
            
            tab_txt = self.font_body.render(tab_name, True, COL_BLACK if i == self.current_tab else COL_TEXT)
            surface.blit(tab_txt, (rect.centerx - tab_txt.get_width() // 2, rect.centery - tab_txt.get_height() // 2))
        
        # Draw appropriate tab content
        if self.current_tab == 0:
            self._draw_general_tab(surface)
        else:
            self._draw_controls_tab(surface)
        
        # Draw Learn more button
        pygame.draw.rect(surface, COL_BLUE, self.learn_more_btn, border_radius=5)
        learn_txt = self.font_body.render("Learn more?", True, COL_WHITE)
        surface.blit(learn_txt, (self.learn_more_btn.centerx - learn_txt.get_width() // 2, 
                                  self.learn_more_btn.centery - learn_txt.get_height() // 2))
        
        # Draw Save button
        pygame.draw.rect(surface, COL_GREEN, self.save_btn, border_radius=5)
        save_txt = self.font_body.render("Save & Exit", True, COL_BLACK)
        surface.blit(save_txt, (self.save_btn.centerx - save_txt.get_width() // 2,
                                 self.save_btn.centery - save_txt.get_height() // 2))
        
        # Draw Back button
        pygame.draw.rect(surface, COL_DARK_RED, self.back_btn, border_radius=5)
        back_txt = self.font_body.render("Back", True, COL_WHITE)
        surface.blit(back_txt, (self.back_btn.centerx - back_txt.get_width() // 2,
                                 self.back_btn.centery - back_txt.get_height() // 2))
        
        # Draw info popup if active
        if self.info_popup.active:
            self.info_popup.draw(surface)
    
    def _draw_general_tab(self, surface):
        """Draw the General (Volume) tab."""
        w = surface.get_width()
        
        # SFX Volume
        sfx_label = self.font_body.render("SFX Volume:", True, COL_TEXT)
        surface.blit(sfx_label, (80, self.volume_sliders["sfx"].centery - sfx_label.get_height() // 2))
        
        # Slider background
        pygame.draw.rect(surface, COL_CARD_BG, self.volume_sliders["sfx"])
        pygame.draw.rect(surface, COL_CARD_BORDER, self.volume_sliders["sfx"], 2)
        
        # Slider fill
        fill_width = int(self.volume_sliders["sfx"].width * self.sfx_volume)
        fill_rect = pygame.Rect(self.volume_sliders["sfx"].x, self.volume_sliders["sfx"].y,
                                fill_width, self.volume_sliders["sfx"].height)
        pygame.draw.rect(surface, COL_LIME, fill_rect)
        
        # SFX Toggle
        toggle_color = COL_GREEN if self.sfx_enabled else COL_DARK_RED
        pygame.draw.rect(surface, toggle_color, self.toggle_btns["sfx"], border_radius=5)
        toggle_txt = "ON" if self.sfx_enabled else "OFF"
        toggle_rend = self.font_body.render(toggle_txt, True, COL_WHITE)
        surface.blit(toggle_rend, (self.toggle_btns["sfx"].centerx - toggle_rend.get_width() // 2,
                                    self.toggle_btns["sfx"].centery - toggle_rend.get_height() // 2))
        
        # Music Volume
        music_label = self.font_body.render("Music Volume:", True, COL_TEXT)
        surface.blit(music_label, (80, self.volume_sliders["music"].centery - music_label.get_height() // 2))
        
        # Slider background
        pygame.draw.rect(surface, COL_CARD_BG, self.volume_sliders["music"])
        pygame.draw.rect(surface, COL_CARD_BORDER, self.volume_sliders["music"], 2)
        
        # Slider fill
        fill_width = int(self.volume_sliders["music"].width * self.music_volume)
        fill_rect = pygame.Rect(self.volume_sliders["music"].x, self.volume_sliders["music"].y,
                                fill_width, self.volume_sliders["music"].height)
        pygame.draw.rect(surface, COL_CYAN, fill_rect)
        
        # Music Toggle
        toggle_color = COL_GREEN if self.music_enabled else COL_DARK_RED
        pygame.draw.rect(surface, toggle_color, self.toggle_btns["music"], border_radius=5)
        toggle_txt = "ON" if self.music_enabled else "OFF"
        toggle_rend = self.font_body.render(toggle_txt, True, COL_WHITE)
        surface.blit(toggle_rend, (self.toggle_btns["music"].centerx - toggle_rend.get_width() // 2,
                                    self.toggle_btns["music"].centery - toggle_rend.get_height() // 2))
        
        # Volume percentage labels
        sfx_pct = self.font_small.render(f"{int(self.sfx_volume * 100)}%", True, COL_TEXT)
        surface.blit(sfx_pct, (self.volume_sliders["sfx"].right + 10, self.volume_sliders["sfx"].top))
        
        music_pct = self.font_small.render(f"{int(self.music_volume * 100)}%", True, COL_TEXT)
        surface.blit(music_pct, (self.volume_sliders["music"].right + 10, self.volume_sliders["music"].top))
    
    def _draw_controls_tab(self, surface):
        """Draw the Controls (Key Bindings) tab."""
        if self.context == "MAIN_MENU":
            # Main menu doesn't have custom bindings
            msg = self.font_body.render("Main menu uses default navigation (Arrow keys, E, T, S)", True, COL_TEXT_MUTED)
            surface.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 200))
            return
 
        if not self.binding_slots:
            # This game (e.g. Guess Number, Memory Match) doesn't have any
            # rebindable keys set up in _init_ui yet - show something instead
            # of just leaving the tab blank
            msg = self.font_body.render(f"{self.context} has no custom key bindings yet", True, COL_TEXT_MUTED)
            surface.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 200))
            return
 
        # Draw binding slots
        for action, key, slot_rect in self.binding_slots:
            # Slot background
            pygame.draw.rect(surface, COL_CARD_BG, slot_rect)
            pygame.draw.rect(surface, COL_CARD_BORDER, slot_rect, 2)
            
            # Action label
            action_txt = self.font_body.render(f"{action}:", True, COL_TEXT)
            surface.blit(action_txt, (slot_rect.x + 10, slot_rect.centery - action_txt.get_height() // 2))
            
            # Key display
            key_name = pygame.key.name(key) if isinstance(key, int) else str(key)
            key_txt = self.font_body.render(f"[{key_name.upper()}]", True, COL_GOLD)
            surface.blit(key_txt, (slot_rect.right - key_txt.get_width() - 10, 
                                   slot_rect.centery - key_txt.get_height() // 2))
            
            # Highlight if being re-bound
            if self.selected_binding and self.selected_binding[2] == slot_rect:
                pygame.draw.rect(surface, COL_YELLOW, slot_rect, 3)
                # Show "Press any key..." message
                wait_txt = self.font_small.render("Press any key...", True, COL_YELLOW)
                surface.blit(wait_txt, (slot_rect.centerx - wait_txt.get_width() // 2,
                                        slot_rect.bottom + 5))
        
        # Instructions
        instr = self.font_small.render("Click a binding to rebind it. Press ESC to cancel.", True, COL_TEXT_MUTED)
        surface.blit(instr, (20, SCREEN_HEIGHT - 120))
    
    def cleanup(self):
        pass
 
