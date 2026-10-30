# assets_loader.py - Finds each game's own cover art, sounds and music.

import os
import re
import pygame

from src.core.game_discovery import discover_games
from src.core.constants import scale_size

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
SOUND_EXTENSIONS = {".wav", ".mp3", ".ogg"}


def _normalise_sound_key(filename):
    """Convert a sound filename into the key the game code can use."""
    stem = os.path.splitext(filename)[0]
    stem = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", stem)
    stem = re.sub(r"[^A-Za-z0-9]+", "_", stem).strip("_").lower()

    # A few old sound names use unusual spelling/capitalisation in the game code.
    aliases = {
        "pwrup_success": "pwrUp_success",
        "card_flip_up": "cardflip_up",
        "card_flip_down": "cardflip_down",
    }
    return aliases.get(stem, stem)


def _load_image(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception:
        # convert_alpha() can fail if a display surface has not been created yet.
        return pygame.image.load(path)


def _make_cover_placeholder(game_name, width, height):
    cover = pygame.Surface((width, height))
    cover.fill((60, 30, 90))
    font = pygame.font.Font(None, scale_size(28))
    lines = game_name.split()
    y = height // 2 - len(lines) * 17
    for line in lines:
        label = font.render(line, True, (235, 235, 235))
        cover.blit(label, (width // 2 - label.get_width() // 2, y))
        y += 34
    return cover


def _find_cover(game_dir):
    """Find a file ending in _boxcover.png/.jpg/.jpeg in the game's own folder."""
    candidates = []
    try:
        for filename in os.listdir(game_dir):
            stem, extension = os.path.splitext(filename)
            if extension.lower() in IMAGE_EXTENSIONS and stem.lower().endswith("_boxcover"):
                candidates.append(os.path.join(game_dir, filename))
    except OSError:
        return None
    return sorted(candidates, key=str.lower)[0] if candidates else None


def load_assets(settings):
    assets = {
        "covers": {},
        "sfx": {},                  # Sounds for the launcher interface only.
        "game_sfx": {},             # Separate sound dictionary for each game.
        "game_music": {},
        "music": {},
        "music_tracks": {},
        "fonts": {},
        "background": None,
    }

    # Look for game folders first. The carousel uses the result of this scan.
    games = discover_games(settings.GAMES_DIR)
    settings.GAME_REGISTRY = games
    settings.GAME_IDS = list(games.keys())
    assets["game_registry"] = games

    # Load fonts.
    font_path = os.path.join(settings.ASSETS_DIR, "fonts", "Press_Start_2P", "PressStart2P-Regular.ttf")
    try:
        assets["fonts"]["main_small"] = pygame.font.Font(font_path, scale_size(16))
        assets["fonts"]["main_medium"] = pygame.font.Font(font_path, scale_size(24))
        assets["fonts"]["main_large"] = pygame.font.Font(font_path, scale_size(48))
        print("[Assets] Loaded the custom font.")
    except Exception as error:
        print(f"[Assets] Could not load custom font: {error}")
        assets["fonts"]["main_small"] = pygame.font.Font(None, scale_size(16))
        assets["fonts"]["main_medium"] = pygame.font.Font(None, scale_size(24))
        assets["fonts"]["main_large"] = pygame.font.Font(None, scale_size(48))

    # Load each game's cover and audio from that game's root folder.
    for game_name, info in games.items():
        game_dir = info["game_dir"]
        cover_path = _find_cover(game_dir)
        if cover_path:
            try:
                cover = _load_image(cover_path)
                cover = pygame.transform.scale(
                    cover, (settings.CAROUSEL_COVER_W, settings.CAROUSEL_COVER_H)
                )
                print(f"[Assets] Cover loaded for {game_name}: {os.path.basename(cover_path)}")
            except Exception as error:
                print(f"[Assets] Could not load {cover_path}: {error}")
                cover = _make_cover_placeholder(game_name, settings.CAROUSEL_COVER_W,
                                                settings.CAROUSEL_COVER_H)
        else:
            print(f"[Assets] No *_boxcover image for {game_name}; using a placeholder.")
            cover = _make_cover_placeholder(game_name, settings.CAROUSEL_COVER_W,
                                            settings.CAROUSEL_COVER_H)
        assets["covers"][game_name] = cover

        game_sfx = {}
        music_candidates = []
        try:
            root_files = sorted(os.listdir(game_dir), key=str.lower)
        except OSError:
            root_files = []

        for filename in root_files:
            path = os.path.join(game_dir, filename)
            if not os.path.isfile(path):
                continue
            stem, extension = os.path.splitext(filename)
            if extension.lower() not in SOUND_EXTENSIONS:
                continue

            # Music files use a clear filename ending: music.wav or *_music.wav.
            if stem.lower() == "music" or stem.lower().endswith("_music"):
                music_candidates.append(path)
                continue

            key = _normalise_sound_key(filename)
            try:
                sound = pygame.mixer.Sound(path)
                game_sfx[key] = sound
                print(f"[Assets] Sound loaded for {game_name}: {filename} -> {key}")
            except Exception as error:
                print(f"[Assets] Could not load sound {path}: {error}")

        assets["game_sfx"][game_name] = game_sfx

        if music_candidates:
            # Prefer a specifically named game_music file, then the first match.
            music_candidates.sort(key=lambda item: (not os.path.basename(item).lower().startswith(info["game_id"].lower() + "_music"), item.lower()))
            music_path = music_candidates[0]
            assets["game_music"][game_name] = music_path
            assets["music_tracks"][game_name] = music_path
            print(f"[Assets] Music found for {game_name}: {os.path.basename(music_path)}")

    # These are launcher sounds, so they stay in the shared assets folder.
    for key, filename in {"menu_nav": "menu_nav.wav", "menu_select": "menu_select.wav"}.items():
        path = os.path.join(settings.SFX_DIR, filename)
        try:
            assets["sfx"][key] = pygame.mixer.Sound(path)
        except Exception as error:
            print(f"[Assets] Could not load launcher sound {filename}: {error}")

    # The menu theme is part of the launcher, not an individual game.
    main_theme = os.path.join(settings.MUSIC_DIR, "main_theme.wav")
    if os.path.isfile(main_theme):
        assets["music_tracks"]["main_theme"] = main_theme

    # Keep a reference to the background class so the menu can create it.
    try:
        from assets.gui.backgrounds.starynight import StarfieldBackground
        assets["background_class"] = StarfieldBackground
    except Exception as error:
        print(f"[Assets] Background could not be loaded: {error}")
        assets["background_class"] = None

    print(
        f"[Assets] Ready: {len(assets['covers'])} games, "
        f"{sum(len(sounds) for sounds in assets['game_sfx'].values())} game sounds, "
        f"{len(assets['music_tracks'])} music tracks."
    )
    return assets
