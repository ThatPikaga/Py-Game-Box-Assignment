# tetris_stats.py — Persistent score storage for Tetris
# Using json like the other data files eventually will

import json
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tetris_stats.json")

DEFAULT = {
    "high_score_1p": 0,
    "high_score_2p_p1": 0,
    "high_score_2p_p2": 0,
    "games_played": 0,
}

def load():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT.copy()

def save(stats):
    with open(DATA_FILE, "w") as f:
        json.dump(stats, f, indent=2)

def update(score_1p=0, score_2p_p1=0, score_2p_p2=0):
    stats = load()
    stats["games_played"] += 1
    if score_1p > stats["high_score_1p"]:
        stats["high_score_1p"] = score_1p
    if score_2p_p1 > stats["high_score_2p_p1"]:
        stats["high_score_2p_p1"] = score_2p_p1
    if score_2p_p2 > stats["high_score_2p_p2"]:
        stats["high_score_2p_p2"] = score_2p_p2
    save(stats)
    return stats
