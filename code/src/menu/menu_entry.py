# menu_entry.py — Represents a single game in the carousel
# Holds metadata: display name, cover image, and the module to launch

import pygame

class MenuEntry:
    def __init__(self, name, cover_surface, module_path, game_class_name):
        self.name = name
        self.cover = cover_surface
        self.module_path = module_path    # e.g. "src.games.pong.main"
        self.game_class_name = game_class_name  # e.g. "PongGame"

    def launch_game(self):
        # Dynamically import and return an instance of the game's class
        import importlib
        mod = importlib.import_module(self.module_path)
        cls = getattr(mod, self.game_class_name)
        return cls()
