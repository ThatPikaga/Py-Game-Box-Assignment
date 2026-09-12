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

    def startup(self, persist):
        self.persist = persist
        self.done = False
        self.next_state = None
        self.mode_select = None
        self._cover_cache = {}

        settings = persist.get("settings")
        assets = persist.get("assets")
        if not settings or not assets:
            print("[CarouselMenu] Missing settings/assets in persist!")
            return

        self.font_title = pygame.font.Font(None, settings.FONT_TITLE_SIZE)
        self.font_body = pygame.font.Font(None, settings.FONT_BODY_SIZE)
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
            self.starfield = StarfieldClass(950, 950, star_count=200)
        else:
            self.starfield = None

        # Sound & Music
        self.sfx = assets.get("sfx", {})
        self.music = assets.get("music_manager", None)

        # Start menu music
        if self.music:
            self.music.play("main_theme")

    def _wrap_index(self, raw):
        """Modulo-wrap a float offset to stay within [0, n)."""
        if self.n == 0:
            return 0.0
        return raw % self.n

    def handle_event(self, event):
        # if mode select is active, route to that instead
        if self.mode_select:
            self.mode_select.handle_event(event)
            if self.mode_select.done:
                self.done = True
                self.next_state = self.mode_select.next_state   # the mode object
                self.mode_select = None
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
                # Scoreboard — placeholder for now
                pass
            elif event.key == pygame.K_s:
                # Settings — placeholder for now
                pass

    def _play_nav(self):
        if self.sfx and "menu_nav" in self.sfx:
            try: self.sfx["menu_nav"].play()
            except: pass

    def _play_select(self):
        if self.sfx and "menu_select" in self.sfx:
            try: self.sfx["menu_select"].play()
            except: pass

    def _launch_game(self):
        """Check if game has modes; if so show mode select, else launch directly."""
        if not self.entries:
            return

        entry = self.entries[self.selected_index]
        game_name = entry["name"]
        module_prefix = entry["module_prefix"]
        print(f"  [Carousel] Selected: {game_name}")

        # Try to import the game's __init__.py to get MODES
        try:
            mod = importlib.import_module(f"{module_prefix}")
            modes = getattr(mod, "MODES", None)
        except Exception as e:
            print(f"  [Carousel] Could not import {module_prefix}: {e}")
            modes = None

        if modes and len(modes) > 0:
            # Game has multiple modes — show mode select screen
            print(f"  [Carousel] {game_name} has modes: {list(modes.keys())}")
            self.mode_select = ModeSelectScreen(game_name, module_prefix, modes)
            self.mode_select.selected_label = list(modes.keys())[0]
        else:
            # No modes — maybe the module has a class we can instantiate directly
            print(f"  [Carousel] {game_name} has no modes, launching default")
            try:
                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if isinstance(attr, type) and attr.__module__ == f"{module_prefix}.__init__":
                        game_instance = attr()
                        self.persist["launched_game"] = game_instance
                        self.persist["game_name"] = game_name
                        self.done = True
                        self.next_state = game_instance
                        return
            except Exception as e:
                print(f"  [Carousel] Error loading default class from {module_prefix}: {e}")

    def update(self, dt):
        # if mode select is active, update that instead
        if self.mode_select:
            self.mode_select.update(dt)
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
        # if mode select is active, draw that instead
        if self.mode_select:
            self.mode_select.draw(surface)
            return

        # ── Background ──
        if self.starfield:
            self.starfield.draw(surface)
        else:
            surface.fill((5, 5, 15))

        if not self.entries:
            return

        W, H = 950, 950
        cw, ch = 400, 400
        gap = 40
        centre_y = 260
        n = self.n

        # ── Interpolation approach ──
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
            y = centre_y + int((1.0 - scale) * 80)

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
                pygame.draw.rect(surface, (255, 215, 0), (x - 3, y - 3, sw + 6, sh + 6), 3, border_radius=4)

        # Title bar
        title_bg = pygame.Rect(0, 0, W, 60)
        pygame.draw.rect(surface, (10, 10, 30), title_bg)
        pygame.draw.rect(surface, (60, 60, 120), title_bg, 2)

        title_text = self.font_title.render("PYCADE", True, (255, 215, 0))
        surface.blit(title_text, (W // 2 - title_text.get_width() // 2, 12))

        # game name under the selected cover
        if self.entries:
            sel_name = self.entries[self.selected_index]["name"]
            name_text = self.font_body.render(sel_name, True, (230, 230, 250))
            surface.blit(name_text, (W // 2 - name_text.get_width() // 2, centre_y + ch + 15))

        # instructions
        instr = self.font_body.render(
            "< L E F T / R I G H T >  to browse    E  to launch    E S C  to quit",
            True, (150, 150, 180)
        )
        surface.blit(instr, (W // 2 - instr.get_width() // 2, H - 50))

    def cleanup(self):
        pass