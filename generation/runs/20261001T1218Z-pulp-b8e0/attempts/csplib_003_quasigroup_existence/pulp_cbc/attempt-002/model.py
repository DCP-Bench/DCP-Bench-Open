"""Quasigroup existence, QG3.m: find a quasigroup of order m, that is an m x m multiplication
table (a Latin square) over the elements 0..m-1 in which every element occurs once in every
row and once in every column, and in which (a * b) * (b * a) = a for all elements a and b.

The model reports the table.
"""
import pulp


def build(instance):
    m = instance["m"]  # order of the quasigroup
    elements = range(m)

    problem = pulp.LpProblem("qg3", pulp.LpMinimize)  # satisfaction: no objective

    # put[a][b][k] = 1 if a * b = k. Every cell holds one element, and quasigroup reads that
    # element back.
    put = pulp.LpVariable.dicts("put", (elements, elements, elements), cat="Binary")
    quasigroup = [[pulp.LpVariable(f"q_{a}_{b}", 0, m - 1, cat="Integer") for b in elements]
                  for a in elements]
    for a in elements:
        for b in elements:
            problem += pulp.lpSum(put[a][b][k] for k in elements) == 1
            problem += quasigroup[a][b] == pulp.lpSum(k * put[a][b][k] for k in elements)

    for k in elements:
        # every element occurs once in every row
        for a in elements:
            problem += pulp.lpSum(put[a][b][k] for b in elements) == 1
        # every element occurs once in every column
        for b in elements:
            problem += pulp.lpSum(put[a][b][k] for a in elements) == 1

    # The QG3.m property: (a * b) * (b * a) = a. pair[a][b][k][l] = 1 if a * b = k and
    # b * a = l. It is tied to the two cells by sums (one value of a * b, one of b * a), so it is
    # 0/1 whenever put is, and needs no binary of its own.
    pair = pulp.LpVariable.dicts("pair", (elements, elements, elements, elements), 0, 1)
    for a in elements:
        for b in elements:
            for k in elements:
                problem += pulp.lpSum(pair[a][b][k][l] for l in elements) == put[a][b][k]
            for l in elements:
                problem += pulp.lpSum(pair[a][b][k][l] for k in elements) == put[b][a][l]

    # If a * b = k and b * a = l, then k * l = a. Conversely, if k * l = a there is exactly one
    # b with a * b = k and b * a = l: the pair (a, b) can be read back from (k, l), since
    # a = k * l and b = l * k, so the pairs (a * b, b * a) run through every pair once. Both
    # directions together: the cell (k, l) holds a exactly when some b gives the pair (k, l).
    # (The converse is implied by the property; it is stated to tighten the relaxation.)
    for k in elements:
        for l in elements:
            for a in elements:
                problem += put[k][l][a] == pulp.lpSum(pair[a][b][k][l] for b in elements)

    return problem, {"quasigroup": quasigroup}
