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
    columns = range(1, n + 1)
    put = pulp.LpVariable.dicts("put", (range(n), columns), cat="Binary")
    costas = [pulp.LpVariable(f"costas_{i}", 1, n, cat="Integer") for i in range(n)]
    for i in range(n):
        problem += pulp.lpSum(put[i][v] for v in columns) == 1
        problem += costas[i] == pulp.lpSum(v * put[i][v] for v in columns)
    for v in columns:
        problem += pulp.lpSum(put[i][v] for i in range(n)) == 1

    # For every lag l = 1..n-2 the differences costas[i + l] - costas[i] are all different
    # (lag n-1 has a single difference). The pair of rows (i, i + l) has marks in columns
    # (u, v), u != v, and its difference is v - u. pair[(l, i)][(u, v)] = 1 if the marks
    # of rows i and i + l are in columns u and v. It is tied to the two rows (the pairs that
    # start in column u add up to put[i][u], those that end in column v to put[i + l][v]),
    # which keeps the relaxation tight; it is continuous, since once put is 0/1 these sums
    # leave a single pair with value 1.
    column_pairs = [(u, v) for u in columns for v in columns if u != v]
    for l in range(1, n - 1):
        pair = {}
        for i in range(n - l):
            for (u, v) in column_pairs:
                pair[(i, u, v)] = pulp.LpVariable(f"pair_{l}_{i}_{u}_{v}", 0, 1)
            for u in columns:
                problem += pulp.lpSum(pair[(i, u, v)] for v in columns if v != u) == put[i][u]
            for v in columns:
                problem += pulp.lpSum(pair[(i, u, v)] for u in columns if u != v) == put[i + l][v]
        # all differences of this lag are different: each difference d is made by at most one pair of rows
        for d in range(-(n - 1), n):
            if d != 0:
                problem += pulp.lpSum(
                    pair[(i, u, v)] for i in range(n - l) for (u, v) in column_pairs if v - u == d) <= 1

    return problem, {"costas": costas}
