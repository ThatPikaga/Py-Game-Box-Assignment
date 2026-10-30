# settings.py - Shared launcher settings, sizes and file paths.
# Individual games keep their own code, cover art, sounds and music in src/games.
# The list of games is discovered at startup, so it is not maintained here.

import os

# Re-export shared game constants so main.py/carousel can get
# everything from one import when convenient.
from src.core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, scale_x, scale_y, scale_size,
    FONT_TITLE_SIZE, FONT_HEADER_SIZE, FONT_BODY_SIZE,
    COL_BG, COL_CARD_BG, COL_CARD_BORDER,
    COL_TEXT, COL_TEXT_MUTED, COL_PLAYER, COL_AI,
    COL_BLACK, COL_WHITE,
)

# == Base Directory ===============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SFX_DIR = os.path.join(ASSETS_DIR, "sfx")
MUSIC_DIR = os.path.join(SFX_DIR, "music")
DATA_DIR = os.path.join(BASE_DIR, "data")

# == Window ========================================================
# SCREEN_WIDTH / SCREEN_HEIGHT now imported from constants.py
FPS = 60
CAPTION = "PyCade - Retro Arcade Box"

# == Carousel ======================================================
CAROUSEL_VISIBLE = 3
CAROUSEL_COVER_W = scale_size(400)
CAROUSEL_COVER_H = scale_size(400)
CAROUSEL_COVER_Y = scale_y(260)
CAROUSEL_GAP = scale_x(40)

# =============== Games ======================================================
# Games are found automatically inside src/games when assets load.
# Each game folder needs an __init__.py; no central list needs editing.
GAMES_DIR = os.path.join(BASE_DIR, "src", "games")
GAME_REGISTRY = {}
GAME_IDS = []
