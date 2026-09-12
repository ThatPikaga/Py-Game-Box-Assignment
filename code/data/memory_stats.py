# memory_stats.py
import json, os
FILE = os.path.join(os.path.dirname(__file__), "memory_stats.json")
DEFAULT = {"games_played": 0, "best_score": 0}
def load():
    try:
        with open(FILE) as f: return json.load(f)
    except: return DEFAULT.copy()
def save(stats):
    with open(FILE, "w") as f: json.dump(stats, f, indent=2)
