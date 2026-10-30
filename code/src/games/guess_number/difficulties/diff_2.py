from ._base import GuessNumberDifficulty


class Difficulty(GuessNumberDifficulty):
    name = "Medium"
    description = "A balanced number guessing challenge."
    max_tries = 10
