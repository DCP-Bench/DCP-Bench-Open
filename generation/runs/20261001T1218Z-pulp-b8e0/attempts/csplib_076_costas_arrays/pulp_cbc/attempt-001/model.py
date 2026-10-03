"""Costas array: place n marks on an n x n grid, one per row and one per column, so that the
n(n-1)/2 vectors between pairs of marks are all different. With costas[i] the column of
the mark in row i, this says: for every lag l, the differences costas[i + l] - costas[i]
are all different.

The model reports the column of the mark in each row (1-based).
"""
import pulp


def build(instance):
    n = instance["n"]

    problem = pulp.LpProblem("costas_array", pulp.LpMinimize)  # satisfaction: no objective

    # costas[i] = column of the mark in row i. A permutation of 1..n, stated as an
    # assignment matrix: put[i][v] = 1 if the mark of row i is in column v.
    put = pulp.LpVariable.dicts("put", (range(n), range(1, n + 1)), cat="Binary")
    costas = [pulp.LpVariable(f"costas_{i}", 1, n, cat="Integer") for i in range(n)]
    for i in range(n):
        problem += pulp.lpSum(put[i][v] for v in range(1, n + 1)) == 1
        problem += costas[i] == pulp.lpSum(v * put[i][v] for v in range(1, n + 1))
    for v in range(1, n + 1):
        problem += pulp.lpSum(put[i][v] for i in range(n)) == 1

    # For every lag l = 1..n-2 the differences costas[i + l] - costas[i] are all different
    # (lag n-1 has a single difference). gap[(l, i)][d] = 1 if costas[i + l] - costas[i] = d.
    # d = 0 cannot occur because the columns are different. The pair of rows (i, i + l) has
    # exactly one difference, and a pair of columns (u, v) in those rows forces its gap v - u.
    for l in range(1, n - 1):
        gap = {}
        for i in range(n - l):
            gap[i] = {d: pulp.LpVariable(f"gap_{l}_{i}_{d}", cat="Binary")
                      for d in range(-(n - 1), n) if d != 0}
            problem += pulp.lpSum(gap[i].values()) == 1
            for u in range(1, n + 1):
                for v in range(1, n + 1):
                    if u != v:
                        problem += gap[i][v - u] >= put[i][u] + put[i + l][v] - 1
        # all differences of this lag are different: each value d is the gap of at most one pair
        for d in range(-(n - 1), n):
            if d != 0:
                problem += pulp.lpSum(gap[i][d] for i in range(n - l)) <= 1

    return problem, {"costas": costas}
