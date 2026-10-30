



# ======[ C A R O U S E L   M E N U ]======
# main game selection screen with starfield background
# arrow keys scroll, E/Enter launches
#
# Dynamic 3-item viewport with infinite looping:
# - Only ever shows 3 covers at a time: left neighbor, selected, right neighbor
# - Draw order (back-to-front): 1st=left neighbor, 2nd=right neighbor, 3rd=selected
# - Scales: selected=1.0, neighbors=0.8, edge=0.6 — interpolated continuously
#   (see _scale_for_dist) instead of snapping between fixed buckets, so nothing
#   pops mid-scroll.
# - Infinite wrapping via modular arithmetic
# - Smooth scrolling interpolates between positions; the per-frame step is
#   clamped so a frame hitch can never cause an overshoot/wobble.

import pygame
import sys
import os
import importlib
from src.menu.mode_select import ModeSelectScreen
from src.menu.name_entry import NameEntryScreen
from src.menu.difficulty_select import DifficultySelectScreen
from src.core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, scale_x, scale_y, scale_size, title_font, body_font

class CarouselMenu:
    # How finely we quantize cover sizes before caching a scaled surface.
    # A few px of quantization is invisible but means we're not calling
    # transform.smoothscale on a full-size cover from scratch every frame.
    COVER_QUANT = 4

    def __init__(self):
        self.name = "MAIN_MENU"
        self.done = False
        self.next_state = None       # can be "MODE_SELECT" or the mode obj directly
        self.persist = {}
        self.selected_index = 0
        self.font_title = None
        self.font_body = None
        self.starfield = None
        self.clock = pygame.time.Clock()

        # for smooth scrolling — tracks a continuous float offset so we can
        # interpolate between integer positions
        self.target_offset = 0.0
        self.current_offset = 0.0
        self.scroll_speed = 0.15

        # cache of pre-scaled cover surfaces, keyed by (entry_idx, w, h)
        self._cover_cache = {}

        # mode select screen we might show
        self.mode_select = None
        
        # name entry screen we might show (comes before mode select)
        self.name_entry = None

        # difficulty select screen we might show (comes after mode select,
        # only if the game has a difficulties/ package - see _has_difficulties)
        self.difficulty_select = None

        # holds the mode instance while difficulty_select is up, so we've
        # got something to attach the chosen difficulty to and launch once
        # the player actually picks one
        self.pending_launch_instance = None
        self.pending_launch_name = None

    def startup(self, persist):
        self.persist = persist
        self.done = False
        self.next_state = None
        self.mode_select = None
        self.name_entry = None
        self.difficulty_select = None
        self.pending_launch_instance = None
        self.pending_launch_name = None
        self._cover_cache = {}

        settings = persist.get("settings")
        assets = persist.get("assets")
        if not settings or not assets:
            print("[CarouselMenu] Missing settings/assets in persist!")
            return

        self.font_title = title_font()
        self.font_body = body_font()
        self.settings = settings

        # Build entries from GAME_REGISTRY
        self.entries = []
        for game_name in settings.GAME_IDS:
            info = settings.GAME_REGISTRY.get(game_name, {})
            cover = assets["covers"].get(game_name)
            if cover is None:
                continue

            self.entries.append({
                "name": game_name,
                "cover": cover,
                "module_prefix": info.get("module", ""),
            })

        self.n = len(self.entries)
        self.selected_index = 0
        self.current_offset = 0.0
        self.target_offset = 0.0

        # Background
        StarfieldClass = assets.get("background_class")
        if StarfieldClass:
            self.starfield = StarfieldClass(SCREEN_WIDTH, SCREEN_HEIGHT, star_count=200)
        else:
            self.starfield = None

        # Sound & Music
        self.sfx = assets.get("sfx", {})
        self.music = assets.get("music_manager", None)

        # A Play Again transition asks the carousel to reopen this game's
        # mode selector directly. The player name stays in persist, so it is
        # never collected again during replay (or when choosing another game).
        replay_game_name = persist.pop("replay_game_name", None)
        if replay_game_name:
            for index, entry in enumerate(self.entries):
                if entry["name"] == replay_game_name:
                    self.selected_index = index
                    self.current_offset = self.target_offset = float(index)
                    module_prefix = entry["module_prefix"]
                    try:
                        mod = importlib.import_module(module_prefix)
                        modes = getattr(mod, "MODES", None)
                        if modes:
                            self.mode_select = ModeSelectScreen(replay_game_name, module_prefix, modes)
                            self.mode_select.selected_label = list(modes.keys())[0]
                    except Exception as exc:
                        print(f"  [Carousel] Could not reopen modes for {replay_game_name}: {exc}")
                    break

        # Start menu music
        if self.music:
            self.music.play("main_theme")

    def _wrap_index(self, raw):
        """Modulo-wrap a float offset to stay within [0, n)."""
        if self.n == 0:
            return 0.0
        return raw % self.n

    def handle_event(self, event):
        # if difficulty select is up, route to that first (it's the last
        # step before actually launching, so it takes priority over
        # everything below it too)
        if self.difficulty_select:
            self.difficulty_select.handle_event(event)
            if self.difficulty_select.done:
                diff_obj = self.difficulty_select.next_state
                self.difficulty_select = None
                if diff_obj is None:
                    # ESC'd out - drop the pending launch, back to browsing
                    self.pending_launch_instance = None
                    self.pending_launch_name = None
                    return
                # stamp the chosen difficulty onto the mode instance and launch -
                # PongBaseMode._apply_difficulty() picks this up in startup()
                self.pending_launch_instance.difficulty = diff_obj
                self.persist["launched_game"] = self.pending_launch_instance
                self.persist["game_name"] = self.pending_launch_name
                self.done = True
                self.next_state = self.pending_launch_instance
                self.pending_launch_instance = None
                self.pending_launch_name = None
            return

        # if name entry is active, route to that first
        if self.name_entry:
            self.name_entry.handle_event(event)
            if self.name_entry.done:
                if self.name_entry.next_state == "MAIN_MENU":
                    # User cancelled - go back to carousel
                    self.name_entry = None
                    return
                
                # Username confirmed - store it and proceed to mode select or launch
                self.persist["player_username"] = self.name_entry.username
                
                # Now check if we should show mode select or launch directly
                game_name = self.name_entry.game_name
                module_prefix = self.persist.get("pending_game_module", "")
                
                try:
                    mod = importlib.import_module(f"{module_prefix}")
                    modes = getattr(mod, "MODES", None)
                except:
                    modes = None
                
                if modes and len(modes) > 0:
                    # Show mode select screen
                    self.mode_select = ModeSelectScreen(game_name, module_prefix, modes)
                    self.mode_select.selected_label = list(modes.keys())[0]
                else:
                    # Launch game directly - single-mode game, no MODES dict
                    game_instance = None
                    try:
                        for attr_name in dir(mod):
                            attr = getattr(mod, attr_name)
                            # classes defined directly in a package's __init__.py
                            # have __module__ == module_prefix, NOT
                            # "module_prefix.__init__" - that was the bug here,
                            # this loop could never actually find anything
                            if (isinstance(attr, type) and
                                    (attr.__module__ == module_prefix or
                                     attr.__module__.startswith(module_prefix + "."))):
                                game_instance = attr()
                                break
                    except Exception as e:
                        print(f"  [Carousel] Error loading default class from {module_prefix}: {e}")

                    if game_instance:
                        self._proceed_to_difficulty_or_launch(game_instance, game_name, module_prefix)
                    else:
                        print(f"  [Carousel] No launchable class found in {module_prefix}")
                
                self.name_entry = None
            return
        
        # if mode select is active, route to that instead
        if self.mode_select:
            self.mode_select.handle_event(event)
            if self.mode_select.done:
                mode_obj = self.mode_select.next_state    # the mode object, or None if ESC'd out
                game_name = self.mode_select.display_name
                module_prefix = self.mode_select.module_prefix
                self.mode_select = None
                if mode_obj is not None:
                    self._proceed_to_difficulty_or_launch(mode_obj, game_name, module_prefix)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.target_offset = self._wrap_index(self.target_offset - 1)
                self._play_nav()
            elif event.key == pygame.K_RIGHT:
                self.target_offset = self._wrap_index(self.target_offset + 1)
                self._play_nav()
            elif event.key in (pygame.K_e, pygame.K_RETURN):
                self._play_select()
                self._launch_game()
            elif event.key == pygame.K_t:
                # Scoreboard - open with current game context
                self._open_scoreboard()
            elif event.key == pygame.K_s:
                # Settings - open with main menu context
                self._open_settings()

    def _play_nav(self):
        if self.sfx and "menu_nav" in self.sfx:
            try: self.sfx["menu_nav"].play()
            except: pass

    def _play_select(self):
        if self.sfx and "menu_select" in self.sfx:
            try: self.sfx["menu_select"].play()
            except: pass

    def _launch_game(self):
        """Check if game has modes; if so show mode select, else launch directly.
        Now shows name entry screen first to collect player username."""
        if not self.entries:
            return

        entry = self.entries[self.selected_index]
        game_name = entry["name"]
        module_prefix = entry["module_prefix"]
        print(f"  [Carousel] Selected: {game_name}")

        # Store module prefix for later use after name entry
        self.persist["pending_game_module"] = module_prefix

        # Once a username exists, go straight to this game's mode selector.
        # This keeps the same player attached to later games and replays.
        if self.persist.get("player_username"):
            try:
                mod = importlib.import_module(module_prefix)
                modes = getattr(mod, "MODES", None)
                if modes:
                    self.mode_select = ModeSelectScreen(game_name, module_prefix, modes)
                    self.mode_select.selected_label = list(modes.keys())[0]
                    return
            except Exception as exc:
                print(f"  [Carousel] Could not load modes for {game_name}: {exc}")

        # The name-entry screen is only required for the first game session.
        self.name_entry = NameEntryScreen(game_name)

    def _has_difficulties(self, module_prefix):
        """
        Check if this game defines the shared difficulty menu. Memory Match
        keeps its own difficulty picker inside the game, so don't show two.
        """
        if module_prefix == "src.games.memory":
            return None
        try:
            diff_mod = importlib.import_module(f"{module_prefix}.difficulties")
            difficulties = getattr(diff_mod, "DIFFICULTIES", None)
            return difficulties if difficulties else None
        except Exception:
            return None

    def _proceed_to_difficulty_or_launch(self, game_instance, game_name, module_prefix):
        """
        Common landing spot once we know exactly which mode we're about
        to launch, whether that came from mode select or the mode-less
        direct-launch path. If the game has a difficulties/ package, show
        difficulty select next; otherwise launch straight away like it
        always used to.
        """
        # Local two-player Scissors Paper Rock has no difficulty options.
        # Launch it immediately after mode selection rather than showing an
        # irrelevant difficulty screen.
        is_spr_two_player = (
            module_prefix == "src.games.spr"
            and getattr(game_instance, "name", "") == "SPR 2 Players"
        )
        difficulties = None if is_spr_two_player else self._has_difficulties(module_prefix)
        if difficulties:
            self.pending_launch_instance = game_instance
            self.pending_launch_name = game_name
            self.difficulty_select = DifficultySelectScreen(game_name, module_prefix, difficulties)
            self.difficulty_select.selected_label = list(difficulties.keys())[0]
        else:
            self.persist["launched_game"] = game_instance
            self.persist["game_name"] = game_name
            self.done = True
            self.next_state = game_instance

    def _open_scoreboard(self):
        """Open scoreboard for the currently selected game."""
        if not self.entries:
            return
        
        entry = self.entries[self.selected_index]
        game_name = entry["name"]
        
        # Set context and launch scoreboard
        self.persist["scoreboard_context"] = game_name
        self.persist["settings_context"] = game_name  # Also set settings context for reference
        self.done = True
        self.next_state = "SCOREBOARD"
        print(f"  [Carousel] Opening scoreboard for {game_name}")
    
    def _open_settings(self):
        """Open settings menu with main menu context."""
        self.persist["settings_context"] = "MAIN_MENU"
        self.persist["context_module"] = None
        self.done = True
        self.next_state = "SETTINGS"
        print("  [Carousel] Opening settings (main menu context)")

    def update(self, dt):
        # if name entry is active, update that first
        if self.name_entry:
            self.name_entry.update(dt)
            return
        
        # if mode select is active, update that instead
        if self.mode_select:
            self.mode_select.update(dt)
            return

        # if difficulty select is up, update that first
        if self.difficulty_select:
            self.difficulty_select.update(dt)
            return    

        # smooth scroll with wrapping — shortest-path interpolation
        if self.n > 0:
            diff = self.target_offset - self.current_offset
            # Normalize to [-n/2, n/2] to take the shortest path around the circle
            if diff > self.n / 2:
                diff -= self.n
            elif diff < -self.n / 2:
                diff += self.n

            if abs(diff) > 0.01:
                # Framerate-independent smoothing, but clamped to 1.0 so a
                # lag spike (big dt) can never move us *past* the target —
                # without this clamp a stutter causes an overshoot, and the
                # next frame corrects the other way, producing a visible
                # wobble right when things are already janky.
                factor = min(1.0, self.scroll_speed * (dt / 16.67))
                self.current_offset = self._wrap_index(self.current_offset + diff * factor)
            else:
                self.current_offset = self.target_offset

        self.selected_index = round(self.current_offset) % self.n if self.n > 0 else 0

        # update starfield
        if self.starfield:
            self.starfield.update()

    # ---------------------------------------------------------------
    # Easing / interpolation helpers
    # ---------------------------------------------------------------

    @staticmethod
    def _lerp(a, b, t):
        return a + (b - a) * t

    @staticmethod
    def _smoothstep(t):
        t = max(0.0, min(1.0, t))
        return t * t * (3 - 2 * t)

    def _scale_for_dist(self, dist):
        """Continuous scale curve: 1.0 at dead-centre, 0.8 at a resting
        neighbor slot, 0.6 at the outer edge of the viewport.

        This lines up exactly with the original 'resting' sizes, but
        interpolates smoothly across the dist=0.5 boundary instead of
        snapping — that snap was the main source of the pop you were
        seeing mid-scroll, since every transition passes through it.
        """
        dist = min(dist, 1.5)
        if dist <= 0.5:
            t = self._smoothstep(dist / 0.5)
            return self._lerp(1.0, 0.8, t)
        else:
            t = self._smoothstep((dist - 0.5) / 1.0)
            return self._lerp(0.8, 0.6, t)

    def _alpha_for_dist(self, dist):
        """Fade covers out as they near the edge of the viewport so they
        don't hard pop in/out of existence at the +/-1.5 clip boundary."""
        if dist <= 1.2:
            return 255
        if dist >= 1.5:
            return 0
        t = self._smoothstep((dist - 1.2) / 0.3)
        return int(self._lerp(255, 0, t))

    def _get_scaled_cover(self, idx, sw, sh):
        """Cache scaled covers on a quantized grid so we're not re-running
        smoothscale on a full-size cover every single frame."""
        q = self.COVER_QUANT
        qw = max(q, (sw // q) * q)
        qh = max(q, (sh // q) * q)
        key = (idx, qw, qh)
        cached = self._cover_cache.get(key)
        if cached is None:
            cached = pygame.transform.smoothscale(self.entries[idx]["cover"], (qw, qh))
            self._cover_cache[key] = cached
        return cached

    def draw(self, surface):
        # if difficulty select is up, draw that first
        if self.difficulty_select:
            self.difficulty_select.draw(surface)
            return

        # if name entry is active, draw that first
        if self.name_entry:
            self.name_entry.draw(surface)
            return
        
        # if mode select is active, draw that instead
        if self.mode_select:
            self.mode_select.draw(surface)
            return

        # == Background ==
        if self.starfield:
            self.starfield.draw(surface)
        else:
            surface.fill((5, 5, 15))

        if not self.entries:
            return

        W, H = SCREEN_WIDTH, SCREEN_HEIGHT
        cw, ch = scale_size(400), scale_size(400)
        gap = scale_x(40)
        centre_y = scale_y(260)
        n = self.n

        # == Interpolation approach ==
        # We treat the carousel as a continuous float offset.
        # For each "slot" (-1 = left, 0 = centre, +1 = right), we figure out
        # which game index belongs there by looking at the integer-rounded
        # selected index, then slide it based on the fractional remainder.
        sel_round = round(self.current_offset)
        sel_frac = self.current_offset - sel_round  # in [-0.5, 0.5]

        centre_idx = sel_round % n
        spacing = int((cw + gap) * 0.7)

        # Build a list of everything visible this frame
        covers_to_draw = []

        for offset in (-1, 0, 1):
            idx = (centre_idx + offset) % n

            # Effective position: the slot position (-1, 0, or +1) shifted
            # by the fractional movement
            effective_offset = offset - sel_frac

            if effective_offset < -1.5 or effective_offset > 1.5:
                continue

            dist = abs(effective_offset)
            alpha = self._alpha_for_dist(dist)
            if alpha <= 0:
                continue

            scale = self._scale_for_dist(dist)
            scaled_w = max(1, int(cw * scale))
            scaled_h = max(1, int(ch * scale))

            base_centre_x = W // 2 + int(effective_offset * spacing)
            x = base_centre_x - scaled_w // 2
            y = centre_y + scale_y(int((1.0 - scale) * 80))

            scaled_cover = self._get_scaled_cover(idx, scaled_w, scaled_h)

            layer = 2 if dist < 0.5 else (1 if dist < 1.5 else 0)
            covers_to_draw.append((layer, idx, x, y, scaled_w, scaled_h, scaled_cover, alpha, offset))

        # Sort by draw layer (lowest first = drawn first = back)
        covers_to_draw.sort(key=lambda c: c[0])

        for layer, idx, x, y, sw, sh, scover, alpha, offset in covers_to_draw:
            scover.set_alpha(alpha)
            surface.blit(scover, (x, y))
            # Gold border stays on whichever cover is in the logical
            # "selected" slot, for the whole time it holds that slot.
            if offset == 0:
                pygame.draw.rect(surface, (255, 215, 0),
                             (x - scale_x(3), y - scale_y(3),
                              sw + scale_x(6), sh + scale_y(6)),
                             scale_size(3), border_radius=scale_size(4))

        # Title bar
        title_bg = pygame.Rect(0, 0, W, scale_y(60))
        pygame.draw.rect(surface, (10, 10, 30), title_bg)
        pygame.draw.rect(surface, (60, 60, 120), title_bg, 2)

        title_text = self.font_title.render("PYCADE", True, (255, 215, 0))
        surface.blit(title_text, (W // 2 - title_text.get_width() // 2, scale_y(12)))

        # game name under the selected cover
        if self.entries:
            sel_name = self.entries[self.selected_index]["name"]
            name_text = self.font_body.render(sel_name, True, (230, 230, 250))
            surface.blit(name_text, (W // 2 - name_text.get_width() // 2, centre_y + ch + scale_y(15)))

        # instructions
        instr = self.font_body.render(
            "< LEFT / RIGHT >  to browse   |   E  to launch   |   ESC  to quit",
            True, (150, 150, 180)
        )
        surface.blit(instr, (W // 2 - instr.get_width() // 2, H - scale_y(50)))

    def cleanup(self):
        pass