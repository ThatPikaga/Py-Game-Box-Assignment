"""Find games by looking through src/games instead of keeping a manual list."""

import importlib
import os
import re


def _name_from_folder(folder_name):
    """Turn a folder like 'my_new_game' into 'My New Game'."""
    return " ".join(part.capitalize() for part in re.split(r"[_\-\s]+", folder_name) if part)


def discover_games(games_dir):
    """Return game information for each importable folder inside src/games."""
    found_games = {}

    if not os.path.isdir(games_dir):
        print(f"[Games] Game folder was not found: {games_dir}")
        return found_games

    for folder_name in sorted(os.listdir(games_dir), key=str.lower):
        game_dir = os.path.join(games_dir, folder_name)
        init_file = os.path.join(game_dir, "__init__.py")

        # A game must be a Python package so the launcher can import its modes.
        if not os.path.isdir(game_dir) or not os.path.isfile(init_file):
            continue
        if folder_name.startswith("_") or folder_name == "__pycache__":
            continue

        module_path = f"src.games.{folder_name}"
        try:
            game_module = importlib.import_module(module_path)
        except Exception as error:
            print(f"[Games] Skipping {folder_name}; it could not be imported: {error}")
            continue

        # GAME_NAME is optional. If it is missing, use the folder name.
        display_name = getattr(game_module, "GAME_NAME", _name_from_folder(folder_name))
        found_games[display_name] = {
            "name": display_name,
            "game_id": folder_name,
            "module": module_path,
            "game_dir": game_dir,
            "modes": getattr(game_module, "MODES", {}),
        }
        print(f"[Games] Found {display_name} in src/games/{folder_name}")

    return found_games
