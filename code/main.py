# main.py - App entry point; runs the core state machine loop
# PyCade Retro Arcade Box

import pygame
import sys
import os

# Make sure we can import from the code directory
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

import settings as SETTINGS
import assets_loader
from src.engine.base_state import BaseState
from src.engine.state_manager import StateManager
from src.engine.music_manager import MusicManager
from src.menu.carousel_menu import CarouselMenu
from src.menu.pause_menu import PauseMenu
from src.menu.settings_menu import SettingsMenu
from src.menu.scoreboard import Scoreboard
from src.core.game_base import GameBase
from src.core.constants import scale_size

# ======[ G A M E   W R A P P E R   S T A T E ]======
# wraps any game mode so the state machine can run it
# the wrapper handles the pause menu, ESC routing, and music

class GameWrapperState(BaseState):
    """
    Takes any GameBase-derived mode object and runs it inside the state
    machine.  The pause menu is handled here - every game gets it for free.
    """

    def __init__(self):
        super().__init__()
        self.game_instance = None
        self.game_name = ""
        self.font_body = None
        self.music = None
        self.pause = PauseMenu()
        self.stats_saved = False

    def startup(self, persist):
        self.persist = persist
        self.done = False
        self.next_state = None
        self.stats_saved = False

        # the game instance could be a mode object from mode_select or
        # the old-style direct class from the carousel
        self.game_instance = persist.get("launched_game")
        self.game_name = persist.get("game_name", "Unknown")
        
        # Grabs medium pixel font, or safely falls back to None if asset loading fails
        loaded_fonts = persist.get("assets", {}).get("fonts", {})
        self.font_body = loaded_fonts.get("main_medium") or pygame.font.Font(None, scale_size(24))
        
        self.music = persist.get("assets", {}).get("music_manager", None)
        self.pause.close()  # ensure pause is off at start

        # The music key is the game's display name, from the folder scan.
        if self.music and self.game_instance:
            if self.game_name in self.persist.get("assets", {}).get("game_music", {}):
                self.music.play(self.game_name)
            else:
                # A game without music should not keep the menu song playing.
                self.music.stop()

        # call startup on the game mode
        if hasattr(self.game_instance, "startup"):
            try:
                self.game_instance.startup(persist)
            except Exception as e:
                print(f"  [Wrapper] startup() failed for {self.game_name}: {e}")

    def handle_event(self, event):
        if not self.game_instance:
            return

        # == pause menu handling ================================
        if self.pause.active:
            game_name = self.persist.get("game_name", "")
            result = self.pause.handle_key(event.key, game_name) if event.type == pygame.KEYDOWN else None
            if result == "RESUME":
                self.pause.close()
            elif result == "MAIN_MENU":
                self.done = True
                self.next_state = "MAIN_MENU"
            elif isinstance(result, tuple) and result[0] == "SETTINGS":
                # Go to settings with game context
                game_context = result[1] if result[1] else self.game_name
                self.persist["settings_context"] = game_context
                self.persist["context_module"] = getattr(self.game_instance.__class__, "__module__", None)
                self.done = True
                self.next_state = "SETTINGS"
            return

        # == normal event routing ==============================
        result = None
        if hasattr(self.game_instance, "handle_event"):
            try:
                result = self.game_instance.handle_event(event)
            except Exception as e:
                print(f"  [Wrapper] handle_event error: {e}")

        # check if the game requested a pause
        if hasattr(self.game_instance, "pause_requested") and self.game_instance.pause_requested:
            self.pause.open()
            self.game_instance.pause_requested = False

        # if handle_event returned a transition request, honour it
        if isinstance(result, str):
            if result in ("MAIN_MENU", "PLAY_AGAIN"):
                self.done = True
                self.next_state = result
                return

        # ESC also works at the wrapper level as fallback
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # if the game didn't handle pause, open it here
            if not self.pause.active:
                self.pause.open()

    def update(self, dt):
        if not self.game_instance:
            return
        if self.pause.active:
            return  # game is frozen

        if hasattr(self.game_instance, "update"):
            try:
                self.game_instance.update(dt)
            except Exception as e:
                print(f"  [Wrapper] update error: {e}")

    def draw(self, surface):
        if not self.game_instance:
            surface.fill((5, 5, 15))
            txt = self.font_body.render(f"Loading: {self.game_name}...", True, (255, 215, 0))
            
            # Dynamically reads settings screen dimensions to pin text dead centre
            screen_w = self.persist["settings"].SCREEN_WIDTH
            surface.blit(txt, (screen_w // 2 - txt.get_width() // 2, 460))
            return

        # draw the game
        if hasattr(self.game_instance, "draw"):
            try:
                self.game_instance.draw(surface)
            except Exception as e:
                print(f"  [Wrapper] draw error: {e}")

        # draw pause overlay on top
        self.pause.draw(surface)


    def cleanup(self):
        """Save the result and stop game music when leaving the game."""
        if not self.stats_saved and self.game_instance:
            from src.core.stats import save_game_result
            save_game_result(
                CODE_DIR,
                self.game_name,
                self.persist.get("player_username", ""),
                self.game_instance,
            )
            self.stats_saved = True

        if self.music:
            self.music.stop(fade_ms=400)
        if hasattr(self.game_instance, "cleanup"):
            try:
                self.game_instance.cleanup()
            except Exception:
                pass


# ======[ M A I N   E N T R Y   P O I N T ]======

def main():
    pygame.init()
    pygame.mixer.init()

    # window setup
    screen = pygame.display.set_mode((SETTINGS.SCREEN_WIDTH, SETTINGS.SCREEN_HEIGHT))
    pygame.display.set_caption(SETTINGS.CAPTION)
    clock = pygame.time.Clock()

    # load all assets
    print("[PyCade] Loading assets...")
    assets = assets_loader.load_assets(SETTINGS)
    print("[PyCade] Assets loaded successfully.")

    # music manager
    assets["music_manager"] = MusicManager(assets.get("music_tracks", {}))

    persist = {
        "settings": SETTINGS,
        "assets": assets,
        "screen": screen,
        "clock": clock,
        "music_manager": assets.get("music_manager"),
    }

    # build states
    carousel = CarouselMenu()
    game_wrapper = GameWrapperState()
    settings_menu = SettingsMenu()
    scoreboard = Scoreboard()

    # Settings and Scoreboard are overlays, so they do not need to be states.
    state_machine = StateManager("MAIN_MENU", {
        "MAIN_MENU": carousel,
        "GAME_WRAPPER": game_wrapper,
    })

    carousel.startup(persist)
    # Load the saved launcher audio settings straight away, not only when the screen opens.
    settings_menu.startup(persist)

    # These screens sit on top of the current screen instead of replacing it.
    settings_overlay = False
    scoreboard_overlay = False

    # main loop
    running = True
    while running:
        dt = clock.tick(SETTINGS.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if settings_overlay:
                settings_menu.handle_event(event)
                continue
            if scoreboard_overlay:
                scoreboard.handle_event(event)
                continue

            # ESC from carousel quits the app
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state_machine.current_name == "MAIN_MENU":
                    # check if mode select, name entry, OR difficulty select is
                    # active - if so, let it handle esc instead of quitting.
                    # difficulty_select is new; same bug as the name_entry one
                    # would've bitten it if it wasn't added here too
                    if not carousel.mode_select and not carousel.name_entry and not carousel.difficulty_select:
                        running = False
                        break

            state_machine.handle_event(event)

        state_machine.update(dt)

        # check if carousel wants to launch a game / show mode select / open a named screen
        if carousel.done and carousel.next_state:
            next_obj = carousel.next_state
            # A game mode launches through the wrapper. Settings and Scoreboard
            # are drawn over the current screen, so opening them does not reset it.
            if isinstance(next_obj, GameBase) or hasattr(next_obj, "startup"):
                persist["launched_game"] = next_obj
                persist["game_name"] = carousel.entries[carousel.selected_index]["name"]
                state_machine.change("GAME_WRAPPER", persist)
            elif next_obj == "SETTINGS":
                settings_menu.startup(persist)
                settings_overlay = True
            elif next_obj == "SCOREBOARD":
                scoreboard.startup(persist)
                scoreboard_overlay = True
            elif isinstance(next_obj, str) and next_obj in state_machine.states:
                state_machine.change(next_obj, persist)
            carousel.done = False
            carousel.next_state = None

        # Game-over Play Again returns to this game's mode selector, not the main carousel.
        if game_wrapper.done and game_wrapper.next_state == "PLAY_AGAIN":
            persist["replay_game_name"] = game_wrapper.game_name
            state_machine.change("MAIN_MENU", persist)
            game_wrapper.done = False
            game_wrapper.next_state = None
        # check if game wrapper wants to go back to the main carousel
        elif game_wrapper.done and game_wrapper.next_state == "MAIN_MENU":
            state_machine.change("MAIN_MENU", persist)
            game_wrapper.done = False
            game_wrapper.next_state = None
        # check if game wrapper wants to open settings (S from the pause menu).
        # this branch didn't exist before, so pressing S while paused set
        # done=True/next_state="SETTINGS" and then just... sat there, since
        # nothing was watching for "SETTINGS" coming from the game wrapper
        elif game_wrapper.done and game_wrapper.next_state == "SETTINGS":
            settings_menu.startup(persist)
            settings_overlay = True
            game_wrapper.done = False
            game_wrapper.next_state = None
        
        # Closing Settings leaves the previous menu/game exactly where it was.
        if settings_overlay and settings_menu.done:
            settings_overlay = False
            settings_menu.done = False
            settings_menu.next_state = None
        
        # Closing either overlay reveals the same menu or game that was underneath.
        if scoreboard_overlay and scoreboard.done:
            scoreboard_overlay = False
            scoreboard.done = False
            scoreboard.next_state = None

        # Draw the active menu or game first, then put any open overlay on top.
        state_machine.draw(screen)
        if settings_overlay:
            settings_menu.draw(screen)
        if scoreboard_overlay:
            scoreboard.draw(screen)
        pygame.display.flip()

    # Save the current game too if the player closes the app straight away.
    state_machine.current.cleanup()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()