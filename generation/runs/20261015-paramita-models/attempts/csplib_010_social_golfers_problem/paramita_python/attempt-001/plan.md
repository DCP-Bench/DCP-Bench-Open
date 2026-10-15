# Plan: csplib_010 social golfers (Paramita, one-hot groups)

Golfers play once a week in groups of group_size; no two golfers share a group twice.
- n_groups * group_size golfers -> golfers G = n_groups * group_size.
- Each golfer plays in one group each week -> one-hot p[i][j][g], exactly one g per (i, j).
- Each group in each week holds group_size golfers -> sum_i p[i][j][g] == group_size.
- Golfers meet at most once -> meet[i][k][j] forced true when both in the same group in week j (clause ~p[i][j][g] | ~p[k][j][g] | meet), then sum_j meet[i][k][j] <= 1.
- Symmetry: golfers in week 0 are interchangeable, so golfer i is in group i // group_size in week 0.
- Output assign[i][j] -> sum(g * p[i][j][g]), 0-based group number.
- Satisfaction problem, no objective.
