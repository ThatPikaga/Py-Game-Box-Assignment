from ._base import GuessNumberDifficulty


class Difficulty(GuessNumberDifficulty):
    name = "Hard"
    description = "You have only a few tries."
    max_tries = 5
