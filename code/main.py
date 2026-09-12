# main.py - App entry point; runs the core state machine loop
# PyCade Retro Arcade Box
#
# Major rework: now supports pause menu (shared across all games),
# dynamic mode selection, and the new GameBase interface.

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

    def startup(self, persist):
        self.persist = persist
        self.done = False
        self.next_state = None

        # the game instance could be a mode object from mode_select or
        # the old-style direct class from the carousel
        self.game_instance = persist.get("launched_game")
        self.game_name = persist.get("game_name", "Unknown")
        self.font_body = pygame.font.Font(None, 28)
        self.music = persist.get("assets", {}).get("music_manager", None)
        self.pause.close()  # ensure pause is off at start

        # Switch to game-specific music
        if self.music and self.game_instance:
            game_music_map = {
                "Breakout":            "breakout",
                "Guess Number":        "guessNumber",
                "Memory Match":        "concentration",
                "Pong":                "pong",
                "Scissors Paper Rock": "spr",
                "Tetris":              "tetris",
            }
            music_key = game_music_map.get(self.game_name)
            if music_key:
                self.music.play(music_key)

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
            result = self.pause.handle_key(event.key) if event.type == pygame.KEYDOWN else None
            if result == "RESUME":
                self.pause.close()
            elif result == "MAIN_MENU":
                self.done = True
                self.next_state = "MAIN_MENU"
            elif result == "SETTINGS":
                # go to settings (stub for now - just resume)
                print("  [Wrapper] Settings from pause - stub, resuming game.")
                self.pause.close()
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
            if result == "MAIN_MENU":
                self.done = True
                self.next_state = "MAIN_MENU"
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
            surface.blit(txt, (475 - txt.get_width() // 2, 460))
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
        """Stop game music when returning to carousel."""
        if self.music:
            self.music.stop(fade_ms=400)
        if hasattr(self.game_instance, "cleanup"):
            try:
                self.game_instance.cleanup()
            except:
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

    state_machine = StateManager("MAIN_MENU", {
        "MAIN_MENU": carousel,
        "GAME_WRAPPER": game_wrapper,
    })

    carousel.startup(persist)

    # main loop
    running = True
    while running:
        dt = clock.tick(SETTINGS.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # ESC from carousel quits the app
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state_machine.current_name == "MAIN_MENU":
                    # check if mode select is active - if so, let it handle esc
                    if not carousel.mode_select:
                        running = False
                        break

            state_machine.handle_event(event)

        state_machine.update(dt)

        # check if carousel wants to launch a game / show mode select
        if carousel.done and carousel.next_state:
            next_obj = carousel.next_state
            # next_state could be a mode object (GameBase) or just the mode_select handled it
            if isinstance(next_obj, GameBase) or hasattr(next_obj, "startup"):
                # it's a game mode object - launch it
                persist["launched_game"] = next_obj
                persist["game_name"] = carousel.entries[carousel.selected_index]["name"]
                state_machine.change("GAME_WRAPPER", persist)
            else:
                # fallback: the old style where next_state was just a name string
                pass
            carousel.done = False
            carousel.next_state = None

        # check if game wrapper wants to go back
        if game_wrapper.done and game_wrapper.next_state == "MAIN_MENU":
            state_machine.change("MAIN_MENU", persist)
            game_wrapper.done = False
            game_wrapper.next_state = None

        # draw
        state_machine.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()