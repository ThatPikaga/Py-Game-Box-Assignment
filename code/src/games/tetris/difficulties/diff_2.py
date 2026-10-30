from ._base import TetrisDifficulty


class Difficulty(TetrisDifficulty):
    name = "Medium"
    description = "The standard falling speed."
    gravity_interval = 500
