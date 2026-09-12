# pong_stats.py
import json, os
FILE = os.path.join(os.path.dirname(__file__), "pong_stats.json")
DEFAULT = {"p1_wins": 0, "p2_wins": 0, "games_played": 0}
def load():
    try:
        with open(FILE) as f: return json.load(f)
    except: return DEFAULT.copy()
def save(stats):
    with open(FILE, "w") as f: json.dump(stats, f, indent=2)
