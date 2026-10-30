from ._base import GuessNumberDifficulty


class Difficulty(GuessNumberDifficulty):
    name = "Easy"
    description = "You get plenty of tries to find the number."
    max_tries = 20
