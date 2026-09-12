# assets_loader.py — Startup routine that loads and scales all images and sounds
# Called once after pygame.init() so everything is ready for the state machine

import pygame
import os

# Import settings inside the function to avoid circular import issues
def load_assets(settings):
    # Load all cover art images, sounds, and backgrounds. Returns a dict."""
    assets = {
        "covers": {},
        "sfx": {},
        "music": {},
        "background": None,
    }

    #  Load cover art 
    for game_name, filename in settings.COVER_FILES.items():
        path = os.path.join(settings.COVER_DIR, filename)
        try:
            try:
                img = pygame.image.load(path).convert()
            except Exception:
                # If convert() fails (e.g. dummy video driver), try without convert
                img = pygame.image.load(path)
            # Scale to carousel size
            img = pygame.transform.scale(img, (settings.CAROUSEL_COVER_W, settings.CAROUSEL_COVER_H))
            assets["covers"][game_name] = img
            print(f"  [OK] Cover loaded: {game_name}")
        except Exception as e:
            print(f"  [!!] Could not load cover {filename}: {e}")
            # Create a placeholder surface so the game doesn't crash
            surf = pygame.Surface((settings.CAROUSEL_COVER_W, settings.CAROUSEL_COVER_H))
            surf.fill((60, 30, 90))
            font = pygame.font.Font(None, 28)
            text = font.render(game_name, True, (200, 200, 200))
            surf.blit(text, (20, 180))
            assets["covers"][game_name] = surf

    #  Import background
    from assets.gui.backgrounds.starynight import StarfieldBackground
    assets["background_class"] = StarfieldBackground

    #  Load SFX 
    sfx_files = {
        "menu_nav":     "menu_nav.wav",
        "menu_select":  "menu_select.wav",
        "pong":         "pong.wav",
        "breakout":     "breakout.wav",
        "spr":          "SPR.wav",
        "concentration":"concentration.wav",
        "guessNumber":  "guessNumber.wav",
        "ball_gone":    "ball_gone.mp3",
        "padel_hit":    "padelHit.wav",
        "life_lost":    "lifeLost.wav",
        "padel_grow":   "padel_grow.wav",
        "padel_shrink": "padel_shrink.wav",
        "pwrUp_success":"pwrUp_success.wav",
        "cardflip_up":  "cardFlip_up.wav",
        "cardflip_down":"cardFlip_down.wav",
        "num_correct":  "num_correct.wav",
        "num_wrong":    "num_wrong.wav",
        "ball_obj_hit": "ballObj_hitwav.wav",
        "ball_metal":   "ballMObj_hit.wav",
    }

    for key, filename in sfx_files.items():
        path = os.path.join(settings.SFX_DIR, filename)
        try:
            snd = pygame.mixer.Sound(path)
            assets["sfx"][key] = snd
        except Exception as e:
            print(f"  [!!] Could not load sfx/{filename}: {e}")

    # Load music tracks 
    # Music files live in sfx/music/ (a subfolder)
    music_files = {
        "main_theme":"main_theme.wav",
        "pong":"pong.wav",
        "spr":"SPR.wav",
        "concentration":"concentration.wav",
        "breakout":"breakout.wav",
        "guessNumber":"guessNumber.wav",
        "tetris":"tetris.wav",
    }
    # Music is loaded via pygame.mixer.music, we just store the paths
    assets["music_tracks"] = {
        k: os.path.join(settings.MUSIC_DIR, v)
        for k, v in music_files.items()
    }

    print(f"  Assets loaded: {len(assets['covers'])} covers, {len(assets['sfx'])} sfx, {len(assets['music_tracks'])} tracks")
    return assets

