# Three coins: starting from the given faces, make all coins face the same way in exactly num_moves moves, where each move flips one coin.
from pycsp3 import *

init = data.init
num_moves = data.num_moves
num_coins = len(init)

# steps[s][j] = 1 if coin j shows tails (1) after s moves, 0 if heads
steps = VarArray(size=[num_moves + 1, num_coins], dom={0, 1})
# flips[s][j] = 1 if coin j is flipped by move s + 1
flips = VarArray(size=[num_moves, num_coins], dom={0, 1})

satisfy(
    # the coins start with the given faces
    [steps[0][j] == init[j] for j in range(num_coins)],
    # each move flips exactly one coin, and the other coins keep their face
    [Table(scope=[steps[s][j], steps[s + 1][j], flips[s][j]], supports=[(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]) for s in range(num_moves) for j in range(num_coins)],
    [Sum(flips[s]) == 1 for s in range(num_moves)],
    # at the end all coins face either all heads or all tails
    [steps[num_moves][j] == steps[num_moves][0] for j in range(1, num_coins)],
)
