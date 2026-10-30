from ._base import TetrisDifficulty


class Difficulty(TetrisDifficulty):
    name = "Hard"
    description = "Pieces fall much faster."
    gravity_interval = 200
