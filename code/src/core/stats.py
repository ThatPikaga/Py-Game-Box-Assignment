"""Save the result from any game without needing a new stats file mapping."""

import json
import os
import re
from datetime import datetime


def _get_number(value, default=0):
    """Convert a value to a number while handling empty or invalid values."""
    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    try:
        number = float(value)
        return int(number) if number.is_integer() else number
    except (TypeError, ValueError):
        return default


def _game_slug(game_name):
    """Use the same safe filename format for any game's scoreboard file."""
    slug = re.sub(r"[^a-z0-9]+", "_", str(game_name).lower()).strip("_")
    return slug or "unknown_game"


def stats_file_path(code_dir, game_name):
    """Return the JSON file path used by both saving and the scoreboard."""
    return os.path.join(code_dir, "data", f"{_game_slug(game_name)}_stats.json")


def _custom_result(game):
    """Use a game's optional standard result method, if it has one."""
    method = getattr(game, "get_scoreboard_data", None)
    if not callable(method):
        return None

    try:
        data = method()
    except Exception as error:
        print(f"[Stats] Game result method failed: {error}")
        return None

    if not isinstance(data, dict):
        return None

    # A score is the simplest result to report. Other games can use a metric name,
    # such as "Wave", "Round", or "Level", with a matching number.
    if "score" in data and data.get("score") is not None:
        metric_label = str(data.get("metric_label") or "Score")
        metric_value = _get_number(data.get("score"), None)
    elif data.get("metric_value") is not None:
        metric_label = str(data.get("metric_label") or "Result")
        metric_value = _get_number(data.get("metric_value"), None)
    else:
        metric_label = None
        metric_value = None

    return {
        "score": metric_value if metric_label and metric_label.lower() == "score" else None,
        "metric_label": metric_label,
        "metric_value": metric_value,
        "wins": _get_number(data.get("wins", 0)),
        "result": str(data.get("result", "Played")),
    }


def get_result(game_name, game):
    """Collect a result from the optional standard method or existing games."""
    result = _custom_result(game)
    if result is not None:
        return result

    # These branches keep the already-built games compatible while they move
    # onto the small get_scoreboard_data() method at their own pace.
    result = {"score": None, "metric_label": None, "metric_value": None,
              "wins": 0, "result": "Played"}

    if game_name == "Breakout":
        result["score"] = _get_number(getattr(game, "score", 0))
        result["result"] = "Game over" if getattr(game, "game_over", False) else "Exited game"

    elif game_name == "Guess Number":
        message = str(getattr(game, "status_message", "")).lower()
        state = str(getattr(game, "state", ""))
        won = state == "GAME_OVER" and (
            "you win" in message or "wins this round" in message or "wins!" in message
        )
        result["score"] = _get_number(getattr(game, "tries_left", 0)) if won else 0
        result["wins"] = int(won)
        result["result"] = "Win" if won else ("Finished" if state == "GAME_OVER" else "Exited game")

    elif game_name == "Memory Match":
        mode_type = type(game).__name__
        if mode_type == "Memory1PMode":
            result["score"] = _get_number(getattr(game, "pairs_found", 0))
            won = (getattr(game, "state", "") == "GAME_OVER" and
                   getattr(game, "pairs_found", 0) == getattr(game, "num_pairs", -1))
        elif mode_type == "Memory2PMode":
            result["score"] = _get_number(getattr(game, "p1_pairs", 0))
            won = getattr(game, "winner_num", 0) == 1
        else:
            result["score"] = _get_number(getattr(game, "player_pairs", 0))
            won = getattr(game, "winner_num", 0) == 1
        result["wins"] = int(won)
        result["result"] = "Win" if won else (
            "Finished" if getattr(game, "state", "") == "GAME_OVER" else "Exited game"
        )

    elif game_name == "Pong":
        if type(game).__name__ == "Pong2PMode":
            player_score = _get_number(getattr(game, "p1_score", 0))
            other_score = _get_number(getattr(game, "p2_score", 0))
        else:
            player_score = _get_number(getattr(game, "player_score", 0))
            other_score = _get_number(getattr(game, "opponent_score", 0))
        result["score"] = player_score
        result["wins"] = int(player_score > other_score)
        result["result"] = "Win" if player_score > other_score else (
            "Draw" if player_score == other_score else "Loss"
        )

    elif game_name == "Scissors Paper Rock":
        winner = str(getattr(game, "winner_text", ""))
        if not winner:
            winner = str(getattr(game, "detail_text", ""))
        won = ("You" in winner and "Win" in winner) or ("Player 1" in winner and "Win" in winner)
        draw = "draw" in winner.lower()
        result["score"] = int(won)
        result["wins"] = int(won)
        result["result"] = "Win" if won else ("Draw" if draw else "Loss")

    elif game_name == "Tetris":
        if type(game).__name__ == "Tetris2PMode":
            result["score"] = _get_number(getattr(getattr(game, "board1", None), "score", 0))
            winner = str(getattr(game, "winner_msg", ""))
            result["wins"] = int("Player 1 Wins" in winner)
            result["result"] = "Win" if result["wins"] else ("Draw" if winner == "Draw!" else "Loss")
        else:
            result["score"] = _get_number(getattr(getattr(game, "board", None), "score", 0))
            result["result"] = "Game over" if getattr(game, "state", "") == "GAME_OVER" else "Exited game"

    # Current games report a score by their existing fields. For a newly added
    # game, the result remains "Played" unless it implements the standard method.
    if result["score"] is not None:
        result["metric_label"] = "Score"
        result["metric_value"] = result["score"]
    return result


def save_game_result(code_dir, game_name, username, game):
    """Save a session for this username. Games do not need a fixed stats mapping."""
    username = str(username or "").strip().upper()[:12]
    if not username or game is None:
        return False

    stats_path = stats_file_path(code_dir, game_name)
    os.makedirs(os.path.dirname(stats_path), exist_ok=True)

    try:
        with open(stats_path, "r", encoding="utf-8") as file:
            all_stats = json.load(file)
        if not isinstance(all_stats, dict):
            all_stats = {}
    except (OSError, json.JSONDecodeError):
        all_stats = {}

    old = all_stats.get(username, {})
    if not isinstance(old, dict):
        old = {}

    this_result = get_result(game_name, game)
    metric_label = this_result.get("metric_label")
    metric_value = this_result.get("metric_value")
    games_played = _get_number(old.get("games_played", 0)) + 1
    wins = _get_number(old.get("wins", 0)) + _get_number(this_result.get("wins", 0))

    # Only compare numbers that describe the same metric. A wave count and a
    # score are not interchangeable, even though both are numeric.
    old_label = old.get("metric_label") or (
        "Score" if old.get("best_score", old.get("score")) is not None else None
    )
    old_best = old.get("best_metric_value")
    if old_best is None:
        old_best = old.get("best_score", old.get("score"))
    old_best = _get_number(old_best, None)

    if metric_value is not None and metric_label:
        if old_label and old_label.lower() == metric_label.lower() and old_best is not None:
            best_metric_value = max(old_best, metric_value)
        else:
            best_metric_value = metric_value
        stored_metric_label = metric_label
    else:
        # If this session did not reach a result, don't erase a previous best.
        best_metric_value = old_best
        stored_metric_label = old_label

    is_score = bool(stored_metric_label and stored_metric_label.lower() == "score"
                    and best_metric_value is not None)
    all_stats[username] = {
        "score": best_metric_value if is_score else None,
        "best_score": best_metric_value if is_score else None,
        "last_score": metric_value if is_score else None,
        "metric_label": stored_metric_label,
        "metric_value": metric_value,
        "best_metric_value": best_metric_value,
        "games_played": games_played,
        "wins": wins,
        "last_result": this_result.get("result", "Played"),
        "last_mode": type(game).__name__,
        "last_played": datetime.now().isoformat(timespec="seconds"),
    }

    try:
        with open(stats_path, "w", encoding="utf-8") as file:
            json.dump(all_stats, file, indent=2)
        print(f"[Stats] Saved {game_name} stats for {username} to {os.path.basename(stats_path)}")
        return True
    except OSError as error:
        print(f"[Stats] Could not save stats for {username}: {error}")
        return False
