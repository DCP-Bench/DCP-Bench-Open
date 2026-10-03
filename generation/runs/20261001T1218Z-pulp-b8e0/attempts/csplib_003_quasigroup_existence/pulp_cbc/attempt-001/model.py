"""Quasigroup existence, QG3.m: find a quasigroup of order m, that is an m x m multiplication
table (a Latin square) over the elements 0..m-1 in which every element occurs once in every
row and once in every column, and in which (a * b) * (b * a) = a for all elements a and b.

The model reports the table.
"""
import pulp


def build(instance):
    m = instance["m"]  # order of the quasigroup

    problem = pulp.LpProblem("qg3", pulp.LpMinimize)  # satisfaction: no objective

    # put[a][b][k] = 1 if a * b = k. Every cell holds one element, and quasigroup reads that
    # element back.
    put = pulp.LpVariable.dicts("put", (range(m), range(m), range(m)), cat="Binary")
    quasigroup = [[pulp.LpVariable(f"q_{a}_{b}", 0, m - 1, cat="Integer") for b in range(m)]
                  for a in range(m)]
    for a in range(m):
        for b in range(m):
            problem += pulp.lpSum(put[a][b][k] for k in range(m)) == 1
            problem += quasigroup[a][b] == pulp.lpSum(k * put[a][b][k] for k in range(m))

    for k in range(m):
        # every element occurs once in every row
        for a in range(m):
            problem += pulp.lpSum(put[a][b][k] for b in range(m)) == 1
        # every element occurs once in every column
        for b in range(m):
            problem += pulp.lpSum(put[a][b][k] for a in range(m)) == 1

    # The QG3.m property: (a * b) * (b * a) = a. If a * b = k and b * a = l, the cell (k, l) of
    # the table holds a: an element chosen by the table itself, so the cell is picked out by
    # the two values (an implication on the pair of choices).
    for a in range(m):
        for b in range(m):
            for k in range(m):
                for l in range(m):
                    problem += put[k][l][a] >= put[a][b][k] + put[b][a][l] - 1

    return problem, {"quasigroup": quasigroup}
