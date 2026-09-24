



# ======[ D I F F I C U L T Y   B A S E 

# Every difficulty file (diff_1.py, diff_2.py, ...) exports a class called
# "Difficulty" that inherits from this - same idea as GameBase, but for
# difficulty tuning instead of the whole game.
#
# On its own this only carries what difficulty_select.py needs to draw
# the menu (a name + a one-line blurb). Each game then makes its own
# subclass (see PongDifficulty in src/games/pong/difficulties/_base.py)
# that adds whatever numbers that specific game's AI/physics reads.
# That's the whole point of this file - a new difficulty for a game
# should be "a few overridden class attributes", not a rewritten game.

class Difficulty:
    name = "Difficulty"    # shown on the select button
    description = ""       # one-liner shown under the buttons
