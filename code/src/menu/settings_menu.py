# settings_menu.py — Settings screen (General, Controls tabs)
# Press S on the carousel or pause menu to open; ENTER to save, ESC to exit
# Handles volume (SFX/Music), toggles, and key bindings per context
# Also includes "Learn more?" button that loads adjacent info.txt files
 
import pygame
import json
import os
 
from src.core.constants import *
 
 
class InfoPopup:
    # scrollable information overlay for the active game or menu.

    def __init__(self):
        self.active = False
        self.text_content = ""
        self.heading = "Game Information"
        self.body_content = ""
        self.font_title = header_font()
        self.font_body = make_font(16)
        self.font_hint = make_font(11)
        self.scroll_offset = 0
        self.max_scroll = 0

    def open(self, info_file_path):
        # Load an info `.txt` file and separate its heading from its body copy."""
        if not info_file_path:
            self.text_content = (
                "Could not locate this game's folder.\n\n"
                "Add an info.txt file to the game's root folder to provide instructions."
            )
        else:
            try:
                with open(info_file_path, "r", encoding="utf-8") as f:
                    self.text_content = f.read().strip()
            except FileNotFoundError:
                self.text_content = (
                    "Information Not Available\n\n"
                    "No info.txt file was found for this game.\n\n"
                    f"Expected location: {info_file_path}\n\n"
                    "Add an info.txt file to this folder to provide game instructions."
                )
            except Exception as e:
                self.text_content = f"Unable to Load Information\n\n{e}"

        source_lines = self.text_content.splitlines()
        while source_lines and not source_lines[0].strip():
            source_lines.pop(0)

        self.heading = source_lines[0].strip() if source_lines else "Game Information"
        self.body_content = "\n".join(source_lines[1:]).strip()
        if not self.body_content:
            self.body_content = "There is no additional information to display."
        self.scroll_offset = 0
        self.max_scroll = 0
        self.active = True

    def close(self):
        self.active = False

    def handle_event(self, event):
        """Handle closing and scrolling while the popup owns input."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.close()
                return True
            if event.key in (pygame.K_UP, pygame.K_w):
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 1)
            elif event.key == pygame.K_PAGEUP:
                self.scroll_offset = max(0, self.scroll_offset - 5)
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 5)
        elif event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(
                0, min(self.max_scroll, self.scroll_offset - event.y * 3)
            )
        return False

    def _wrap_body(self, max_width):
        """Wrap paragraphs to the content panel while preserving paragraph gaps."""
        wrapped = []
        for paragraph in self.body_content.splitlines():
            if not paragraph.strip():
                wrapped.append("")
                continue

            words = paragraph.split()
            current_line = ""
            for word in words:
                candidate = f"{current_line} {word}".strip()
                if self.font_body.size(candidate)[0] <= max_width:
                    current_line = candidate
                    continue

                if current_line:
                    wrapped.append(current_line)
                    current_line = ""

                # Split an unusually long word so it cannot spill outside the panel.
                if self.font_body.size(word)[0] <= max_width:
                    current_line = word
                else:
                    chunk = ""
                    for char in word:
                        if chunk and self.font_body.size(chunk + char)[0] > max_width:
                            wrapped.append(chunk)
                            chunk = char
                        else:
                            chunk += char
                    current_line = chunk

            if current_line:
                wrapped.append(current_line)

        return wrapped or ["There is no additional information to display."]

    def draw(self, surface):
        if not self.active:
            return

        w, h = surface.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((4, 5, 18, 218))
        surface.blit(overlay, (0, 0))

        # Use a large, centred panel with a subtle shadow and generous margins.
        margin_x = max(scale_x(28), 12)
        margin_y = max(scale_y(28), 12)
        box_w = max(1, min(scale_x(1040), w - margin_x * 2))
        box_h = max(1, min(scale_y(790), h - margin_y * 2))
        box_rect = pygame.Rect(
            (w - box_w) // 2, (h - box_h) // 2, box_w, box_h
        )
        corner = max(1, scale_size(14))
        shadow_rect = box_rect.move(scale_size(7), scale_size(9))
        pygame.draw.rect(surface, (0, 0, 0), shadow_rect, border_radius=corner)
        pygame.draw.rect(surface, COL_CARD_BG, box_rect, border_radius=corner)
        pygame.draw.rect(
            surface, COL_CARD_BORDER, box_rect, max(1, scale_size(2)),
            border_radius=corner
        )

        # A narrow gold accent makes the top edge and title area feel deliberate.
        accent_rect = pygame.Rect(
            box_rect.left + scale_size(3),
            box_rect.top + scale_size(3),
            max(1, box_rect.width - scale_size(6)),
            max(1, scale_y(5))
        )
        pygame.draw.rect(surface, COL_GOLD, accent_rect, border_radius=corner)

        pad_x = min(scale_x(38), max(12, box_rect.width // 12))
        kicker = self.font_hint.render("GAME GUIDE", True, COL_TEXT_MUTED)
        surface.blit(kicker, (box_rect.left + pad_x, box_rect.top + scale_y(25)))

        title = self.font_title.render(self.heading, True, COL_GOLD)
        title_x = box_rect.left + pad_x
        title_y = box_rect.top + scale_y(52)
        surface.blit(title, (title_x, title_y))

        close_hint = self.font_hint.render("ESC / ENTER  ·  CLOSE", True, COL_TEXT_MUTED)
        surface.blit(
            close_hint,
            (box_rect.right - pad_x - close_hint.get_width(),
             box_rect.top + scale_y(58))
        )

        header_rule_y = box_rect.top + scale_y(105)
        pygame.draw.line(
            surface, COL_CARD_BORDER,
            (box_rect.left + pad_x, header_rule_y),
            (box_rect.right - pad_x, header_rule_y),
            max(1, scale_size(1))
        )

        # Instructions sit in their own inset panel instead of being packed
        # directly against the popup edges.
        content_rect = pygame.Rect(
            box_rect.left + pad_x,
            header_rule_y + scale_y(22),
            max(1, box_rect.width - pad_x * 2),
            max(1, box_rect.bottom - (header_rule_y + scale_y(22)) - scale_y(78))
        )
        pygame.draw.rect(
            surface, COL_BG, content_rect, border_radius=max(1, scale_size(9))
        )
        pygame.draw.rect(
            surface, COL_BOARD_BDR, content_rect, max(1, scale_size(1)),
            border_radius=max(1, scale_size(9))
        )

        inset_x = scale_x(28)
        inset_y = scale_y(25)
        scrollbar_space = scale_x(24)
        text_x = content_rect.left + inset_x
        text_width = max(
            1, content_rect.width - inset_x * 2 - scrollbar_space
        )
        lines = self._wrap_body(text_width)
        line_step = max(self.font_body.get_linesize() + scale_y(11), scale_y(30))
        available_height = max(1, content_rect.height - inset_y * 2)
        visible_count = max(1, available_height // line_step)
        self.max_scroll = max(0, len(lines) - visible_count)
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

        visible_lines = lines[self.scroll_offset:self.scroll_offset + visible_count]
        y = content_rect.top + inset_y
        for line in visible_lines:
            if line:
                text_surface = self.font_body.render(line, True, COL_TEXT)
                surface.blit(text_surface, (text_x, y))
            y += line_step

        # Only show the scrollbar when there is actually more to read.
        if self.max_scroll > 0:
            track_x = content_rect.right - scale_x(13)
            track_y = content_rect.top + inset_y
            track_h = max(1, content_rect.height - inset_y * 2)
            track = pygame.Rect(track_x, track_y, max(2, scale_x(3)), track_h)
            pygame.draw.rect(surface, COL_BOARD_BDR, track, border_radius=3)
            thumb_h = max(scale_y(34), int(track_h * visible_count / len(lines)))
            thumb_h = min(track_h, thumb_h)
            travel = max(0, track_h - thumb_h)
            thumb_y = track_y + int(
                travel * self.scroll_offset / max(1, self.max_scroll)
            )
            thumb = pygame.Rect(track_x - scale_x(2), thumb_y, max(4, scale_x(7)), thumb_h)
            pygame.draw.rect(surface, COL_GOLD, thumb, border_radius=4)

        # A separate footer keeps the keyboard/mouse help away from the body.
        footer_y = box_rect.bottom - scale_y(52)
        pygame.draw.line(
            surface, COL_CARD_BORDER,
            (box_rect.left + pad_x, footer_y - scale_y(12)),
            (box_rect.right - pad_x, footer_y - scale_y(12)),
            max(1, scale_size(1))
        )
        footer_text = (
            "SCROLL:  UP / DOWN  ·  PAGE UP / DOWN  ·  MOUSE WHEEL"
            if self.max_scroll > 0 else "GAME INFORMATION"
        )
        footer = self.font_hint.render(footer_text, True, COL_TEXT_MUTED)
        surface.blit(footer, (box_rect.left + pad_x, footer_y))
        surface.blit(
            close_hint,
            (box_rect.right - pad_x - close_hint.get_width(), footer_y)
        )

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
        # Load settings for current context from JSON file.
        os.makedirs(self.settings_dir, exist_ok=True)
        settings_file = self._get_settings_file()
        
        default_settings = {
            "sfx_volume": 0.1,
            "music_volume": 0.3,
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
        # Apply volume/toggle settings to both launcher and game sounds.
        assets = self.persist.get("assets", {})
        sound_groups = [assets.get("sfx", {}).values()]
        sound_groups.extend(group.values() for group in assets.get("game_sfx", {}).values())

        # Sound objects are loaded once, so changing Settings updates the same objects games use.
        seen_sounds = set()
        sound_volume = self.sfx_volume if self.sfx_enabled else 0.0
        if self.sfx_enabled:
            try:
                pygame.mixer.set_num_channels(16)
            except Exception:
                pass
        for group in sound_groups:
            for sound in group:
                if id(sound) in seen_sounds:
                    continue
                seen_sounds.add(id(sound))
                try:
                    sound.set_volume(sound_volume)
                except Exception:
                    pass

        if not self.sfx_enabled:
            # Stop any sound effect that was already playing when it was muted.
            try:
                pygame.mixer.stop()
            except Exception:
                pass

        music_mgr = assets.get("music_manager")
        if music_mgr:
            music_mgr.set_volume(self.music_volume)
            music_mgr.set_enabled(self.music_enabled)

    def startup(self, persist):
        self.persist = persist
        self.done = False
        self.next_state = None
        self.font_title = title_font()
        self.font_body = body_font()
        self.font_small = make_font(18)
        
        # get context from persist (which state opened settings)
        self.context = persist.get("settings_context", "MAIN_MENU")
        self.context_module = persist.get("context_module", None)
        
        # load settings for this context
        self._load_settings()
        
        # initialise UI elements
        self._init_ui()
        

        self._apply_audio_settings()
    
    def _init_ui(self):
        # initialise UI element positions relative to the settings panel.
        w, h = SCREEN_WIDTH, SCREEN_HEIGHT
        self.panel_rect = pygame.Rect(
            scale_x(100), scale_y(8),
            max(scale_x(1), w - scale_x(200)),
            max(scale_y(1), h - scale_y(16)),
        )
        panel = self.panel_rect

        # Tab buttons, centred inside the panel
        tab_w, tab_h = scale_x(150), scale_y(40)
        tab_y = panel.top + scale_y(70)
        self.tab_btns = [
            pygame.Rect(panel.centerx - tab_w - scale_x(10), tab_y, tab_w, tab_h),
            pygame.Rect(panel.centerx + scale_x(10), tab_y, tab_w, tab_h),
        ]

        # Volume rows and their controls (General tab). The slider, percentage,
        # and toggle are laid out in one row so nothing overlaps or spills out.
        row_x = panel.left + scale_x(20)
        row_w = panel.width - scale_x(40)
        row_h = scale_y(56)
        slider_h = scale_y(20)
        toggle_w, toggle_h = scale_x(80), scale_y(35)
        toggle_x = row_x + row_w - scale_x(100)
        slider_x = row_x + scale_x(190)
        slider_w = max(scale_x(120), toggle_x - slider_x - scale_x(100))
        slider_positions = {"sfx": scale_y(180), "music": scale_y(260)}
        self.volume_rows = {}
        self.volume_sliders = {}
        self.toggle_btns = {}
        for key, slider_y in slider_positions.items():
            row_y = slider_y - scale_y(18)
            self.volume_rows[key] = pygame.Rect(row_x, row_y, row_w, row_h)
            self.volume_sliders[key] = pygame.Rect(slider_x, slider_y, slider_w, slider_h)
            self.toggle_btns[key] = pygame.Rect(
                toggle_x, slider_y + (slider_h - toggle_h) // 2, toggle_w, toggle_h
            )

        # Footer actions are all kept inside the panel with even side margins.
        button_y = panel.bottom - scale_y(65)
        self.learn_more_btn = pygame.Rect(
            panel.right - scale_x(20) - scale_x(190),
            button_y, scale_x(190), scale_y(40)
        )
        self.save_btn = pygame.Rect(
            panel.centerx - scale_x(80), button_y, scale_x(160), scale_y(45)
        )
        self.back_btn = pygame.Rect(
            panel.left + scale_x(20), button_y, scale_x(100), scale_y(40)
        )

        # Binding slots (Controls tab), centred and inset from panel edges
        self.binding_slots = []
        if self.context != "MAIN_MENU":
            
            # Create binding slot rects
            y_offset = panel.top + scale_y(170)
            slot_w = min(scale_x(560), panel.width - scale_x(60))
            slot_x = panel.centerx - slot_w // 2
            for i, (action, key) in enumerate(self.bindings.items()):
                slot_rect = pygame.Rect(
                    slot_x, y_offset + i * scale_y(50), slot_w, scale_y(40)
                )
                self.binding_slots.append((action, key, slot_rect))
    
    def handle_event(self, event):
        # Handle info popup first if active
        if self.info_popup.active:
            if self.info_popup.handle_event(event):
                return  # Popup handled it
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._save_settings()
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
                    self._save_settings()
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
                            self._save_settings()
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
                            self._save_settings()
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
        """Load info.txt from the active game's root folder or the menu folder."""
        menu_dir = os.path.dirname(os.path.abspath(__file__))
        if self.context == "MAIN_MENU":
            info_path = os.path.join(menu_dir, "info.txt")
        else:
            module_parts = (self.context_module or "").split(".")
            if len(module_parts) >= 3 and module_parts[:2] == ["src", "games"]:
                game_folder = module_parts[2]
                game_dir = os.path.abspath(
                    os.path.join(menu_dir, "..", "games", game_folder)
                )
                info_path = os.path.join(game_dir, "info.txt")
            else:
                info_path = None

        self.info_popup.open(info_path)
    
    def update(self, dt):
        # Update binding wait timer
        if self.selected_binding:
            self.binding_wait_timer -= 1
            if self.binding_wait_timer <= 0:
                self.selected_binding = None
    
    def draw(self, surface):
        w, h = surface.get_size()

        # Dim the screen behind settings instead of replacing it completely.
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        surface.blit(overlay, (0, 0))
        panel = self.panel_rect
        pygame.draw.rect(surface, COL_BG, panel, border_radius=10)
        pygame.draw.rect(surface, COL_CARD_BORDER, panel, 2, border_radius=10)

        # Separate the heading from the tab content and keep context in-panel.
        title = self.font_title.render("SETTINGS", True, COL_GOLD)
        surface.blit(title, title.get_rect(center=(panel.centerx, panel.top + scale_y(30))))
        context_label = "Main Menu" if self.context == "MAIN_MENU" else self.context
        ctx_txt = self.font_small.render(context_label, True, COL_TEXT_MUTED)
        surface.blit(ctx_txt, (panel.right - ctx_txt.get_width() - scale_x(20),
                               panel.top + scale_y(20)))
        pygame.draw.line(
            surface, COL_CARD_BORDER,
            (panel.left + scale_x(20), panel.top + scale_y(58)),
            (panel.right - scale_x(20), panel.top + scale_y(58)), 1
        )
        
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
        # Draw the General (Volume) tab with aligned, inset control rows.
        for key, label, volume, enabled, fill_colour in (
            ("sfx", "SFX Volume", self.sfx_volume, self.sfx_enabled, COL_LIME),
            ("music", "Music Volume", self.music_volume, self.music_enabled, COL_CYAN),
        ):
            row = self.volume_rows[key]
            slider = self.volume_sliders[key]
            toggle = self.toggle_btns[key]

            # Subtle row panel keeps each label and its controls visually grouped.
            pygame.draw.rect(surface, COL_CARD_BG, row, border_radius=8)
            pygame.draw.rect(surface, COL_CARD_BORDER, row, 1, border_radius=8)

            label_surf = self.font_body.render(label, True, COL_TEXT)
            surface.blit(label_surf, label_surf.get_rect(
                midleft=(row.left + scale_x(15), row.centery)
            ))

            pygame.draw.rect(surface, COL_CARD_BG, slider, border_radius=5)
            pygame.draw.rect(surface, COL_CARD_BORDER, slider, 1, border_radius=5)
            fill_width = int(slider.width * volume)
            if fill_width > 0:
                fill_rect = pygame.Rect(slider.x, slider.y, fill_width, slider.height)
                pygame.draw.rect(surface, fill_colour, fill_rect, border_radius=5)

            pct = self.font_small.render(f"{int(volume * 100)}%", True, COL_TEXT)
            surface.blit(pct, pct.get_rect(
                midleft=(slider.right + scale_x(8), row.centery)
            ))

            toggle_colour = COL_GREEN if enabled else COL_DARK_RED
            pygame.draw.rect(surface, toggle_colour, toggle, border_radius=6)
            toggle_text = self.font_body.render("ON" if enabled else "OFF", True, COL_WHITE)
            surface.blit(toggle_text, toggle_text.get_rect(center=toggle.center))
    
    def _draw_controls_tab(self, surface):
        if self.context == "MAIN_MENU":
            # Main menu doesn't have custom bindings
            msg = self.font_body.render("Main menu uses default navigation (Arrow keys, E, T, S)", True, COL_TEXT_MUTED)
            surface.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, scale_y(200)))
            return
 
        if not self.binding_slots:
            # If game doesn't have anyvrebindable keys set up in _init_ui yet
            # show something instead of just leaving the tab blank
            msg = self.font_body.render(f"{self.context} has no custom key bindings yet", True, COL_TEXT_MUTED)
            surface.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, scale_y(200)))
            return
 
        # Draw binding slots
        for action, key, slot_rect in self.binding_slots:
            # Slot background
            pygame.draw.rect(surface, COL_CARD_BG, slot_rect)
            pygame.draw.rect(surface, COL_CARD_BORDER, slot_rect, 2)
            
            # Action label
            action_txt = self.font_body.render(f"{action}:", True, COL_TEXT)
            surface.blit(action_txt, (slot_rect.x + scale_x(10), slot_rect.centery - action_txt.get_height() // 2))
            
            # Key display
            key_name = pygame.key.name(key) if isinstance(key, int) else str(key)
            key_txt = self.font_body.render(f"[{key_name.upper()}]", True, COL_GOLD)
            surface.blit(key_txt, (slot_rect.right - key_txt.get_width() - scale_x(10), 
                                   slot_rect.centery - key_txt.get_height() // 2))
            
            # Highlight if being re-bound
            if self.selected_binding and self.selected_binding[2] == slot_rect:
                pygame.draw.rect(surface, COL_YELLOW, slot_rect, 3)
                # Show "Press any key..." message
                wait_txt = self.font_small.render("Press any key...", True, COL_YELLOW)
                surface.blit(wait_txt, (slot_rect.centerx - wait_txt.get_width() // 2,
                                        slot_rect.bottom + scale_y(5)))
        
        # Instructions
        instr = self.font_small.render("Click a binding to rebind it. Press ESC to cancel.", True, COL_TEXT_MUTED)
        surface.blit(instr, (self.panel_rect.left + scale_x(20), SCREEN_HEIGHT - scale_y(120)))
    
    def cleanup(self):
        pass
 
