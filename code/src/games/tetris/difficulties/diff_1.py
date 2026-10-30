from ._base import TetrisDifficulty


class Difficulty(TetrisDifficulty):
    name = "Easy"
    description = "Pieces fall slower."
    gravity_interval = 700
