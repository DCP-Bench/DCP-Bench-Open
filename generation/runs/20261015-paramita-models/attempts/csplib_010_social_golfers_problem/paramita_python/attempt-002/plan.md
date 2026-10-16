# Plan: csplib_010 social golfers, attempt 2 (adds exact meeting counts)

Attempt 1 timed out on json:4 (10 golfers, 8 weeks, groups of 2). Tighter meeting constraints.
- Golfers play once a week in groups of group_size -> one-hot p[i][j][g], exactly one g per (i, j).
- Each group in each week holds group_size golfers -> sum_i p[i][j][g] == group_size.
- Golfers i and k meet at most once -> meet[i][k][j] forced by a shared group, sum_j meet <= 1.
- Meet is exact -> meet[i][k][j] implies a shared group (clause ~meet | ~p_i | p_k per group), so counts are true counts.
- Each golfer meets group_size - 1 others each week -> sum_k meet[i][k][j] == group_size - 1.
- Symmetry: week 0 numbering, golfer i in group i // group_size.
- Output assign[i][j] -> sum(g * p[i][j][g]), 0-based group number.
- Satisfaction problem, no objective.
