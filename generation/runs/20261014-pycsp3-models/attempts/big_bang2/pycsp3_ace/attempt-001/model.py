from pycsp3 import *

# five dice, row 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock; six faces each with values 1 to 12
dice = VarArray(size=[5, 6], dom=range(1, 13))

# the ten 'beats' relationships as (winner, loser) pairs of dice indices
beats = [(0, 2), (0, 3), (1, 0), (1, 4), (2, 1), (2, 3), (3, 1), (3, 4), (4, 0), (4, 2)]

# gt[k][i][j] is 1 when face i of the winner of beats k is larger than face j of the loser
gt = VarArray(size=[len(beats), 6, 6], dom={0, 1})

conds = []
for a in range(5):
    # the order of the faces on one die does not change any comparison, so the faces are sorted
    conds.append(Increasing(dice[a]))

for k, (a, b) in enumerate(beats):
    for i in range(6):
        for j in range(6):
            conds.append((gt[k][i][j] == 1) == (dice[a][i] > dice[b][j]))
    # the winner has a larger face value than the loser in more than half of all 36 pairs of faces
    conds.append(Sum(gt[k][i][j] for i in range(6) for j in range(6)) >= 19)

# the reverse direction of each pair is not a beats relationship: it holds automatically, because
# with at least 19 of 36 pairs won by one die, the other die wins at most 17 of them.
satisfy(conds)
