# settings.py - Central config for PyCade
# Paths, window sizes, colours, FPS - everything in one place
# Once you set it here, every game and the carousel reads it
#
# Game-logic constants (colours, sizes, tetris shapes etc.) live in
# src/core/constants.py and are *the* source of truth.  This file
# imports those shared values and only adds operational config:
# asset paths, the game registry, and carousel layout.

import os

# Re-export shared game constants so main.py/carousel can get
# everything from one import when convenient.
from src.core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
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
GUI_DIR = os.path.join(ASSETS_DIR, "gui")
COVER_DIR = os.path.join(GUI_DIR, "cover-art")
BG_DIR = os.path.join(GUI_DIR, "backgrounds")
DATA_DIR = os.path.join(BASE_DIR, "data")

# == Window ========================================================
# SCREEN_WIDTH / SCREEN_HEIGHT now imported from constants.py
FPS = 60
CAPTION = "PyCade - Retro Arcade Box"

# == Fonts ========================================================
# FONT_TITLE_SIZE, FONT_HEADER_SIZE, FONT_BODY_SIZE imported from constants

# == Carousel ======================================================
CAROUSEL_VISIBLE = 3
CAROUSEL_COVER_W = 400
CAROUSEL_COVER_H = 400
CAROUSEL_COVER_Y = 260
CAROUSEL_GAP = 40

# == Game Registry ========================================
# Order determines position in the carousel
# Each entry: display_name -> (module_prefix, cover_filename)
# The game's __init__.py exports MODES so the mode select screen works

GAME_REGISTRY = {
    "Breakout": {
        "module": "src.games.breakout",
        "cover":  "Breakout.png",
    },
    "Guess Number": {
        "module": "src.games.guess_number",
        "cover":  "Guess Number.png",
    },
    "Memory Match": {
        "module": "src.games.memory",
        "cover":  "Memory Match.png",
    },
    "Pong": {
        "module": "src.games.pong",
        "cover":  "pong.png",
    },
    "Scissors Paper Rock": {
        "module": "src.games.spr",
        "cover":  "Scissors Paper Rock.png",
    },
    "Tetris": {
        "module": "src.games.tetris",
        "cover":  "Tetris.png",
    },
}

GAME_IDS = list(GAME_REGISTRY.keys())

# Map display names to image filenames (for backward compat with assets_loader)
COVER_FILES = {name: info["cover"] for name, info in GAME_REGISTRY.items()}