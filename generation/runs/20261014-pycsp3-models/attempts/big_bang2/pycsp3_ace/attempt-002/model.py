from pycsp3 import *

# five nontransitive dice: row 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock; six faces each, values 1 to 12
dice = VarArray(size=[5, 6], dom=range(1, 13))

# the ten 'beats' relationships as (winner, loser) pairs of dice indices
beats = [(0, 2), (0, 3), (1, 0), (1, 4), (2, 1), (2, 3), (3, 1), (3, 4), (4, 0), (4, 2)]

conds = []
for a in range(5):
    # the order of the faces on one die does not change any comparison, so the faces are sorted
    conds.append(Increasing(dice[a]))

for (a, b) in beats:
    # the winner has a larger face value than the loser in more than half of all 36 pairs of faces
    conds.append(Sum(dice[a][i] > dice[b][j] for i in range(6) for j in range(6)) >= 19)

# the reverse of each beats relationship needs no constraint: the two dice have 36 pairs of faces,
# so with at least 19 won by one die, the other die wins at most 17 of them.
satisfy(conds)
