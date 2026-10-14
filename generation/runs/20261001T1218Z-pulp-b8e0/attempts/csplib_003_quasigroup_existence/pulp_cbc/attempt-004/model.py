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

    # put[a][b][k] = 1 if a * b = k. Every cell holds one element.
    put = pulp.LpVariable.dicts("put", (elements, elements, elements), cat="Binary")
    for a in elements:
        for b in elements:
            problem += pulp.lpSum(put[a][b][k] for k in elements) == 1
    quasigroup = [[pulp.lpSum(k * put[a][b][k] for k in elements) for b in elements]
                  for a in elements]

    for k in elements:
        # every element occurs once in every row
        for a in elements:
            problem += pulp.lpSum(put[a][b][k] for b in elements) == 1
        # every element occurs once in every column
        for b in elements:
            problem += pulp.lpSum(put[a][b][k] for a in elements) == 1

    # The QG3.m property: (a * b) * (b * a) = a. If a * b = k and b * a = l, then k * l = a.
    # Two more implications follow from it with the Latin square, and are stated so that
    # fixing any two of the three cells fixes the third: if a * b = k and k * l = a, then
    # k * (b * a) = a = k * l, so b * a = l (an element occurs once in row k); and if
    # b * a = l and k * l = a, then (a * b) * l = a = k * l, so a * b = k (once in column l).
    for a in elements:
        for b in elements:
            for k in elements:
                for l in elements:
                    problem += put[k][l][a] >= put[a][b][k] + put[b][a][l] - 1
                    problem += put[b][a][l] >= put[a][b][k] + put[k][l][a] - 1
                    problem += put[a][b][k] >= put[b][a][l] + put[k][l][a] - 1

    # Symmetry breaking, derived here (the reference states none). Renaming the elements
    # by any permutation turns a QG3 table into another QG3 table, so m! tables are one up
    # to renaming. The diagonal a -> a * a is an involution, because the property with
    # b = a gives (a * a) * (a * a) = a. Every involution can be renamed into the form
    # (0 1)(2 3)...(2t-2 2t-1) with the elements from 2t on fixed, for some t. So the model
    # asks for that diagonal and lets the solver choose t: swapped[i] = 1 if elements 2i and
    # 2i+1 are swapped by the diagonal, with the swapped pairs first. Every QG3 table has a
    # renamed copy of this form, and every table reported is still a QG3 table.
    half = m // 2
    swapped = [pulp.LpVariable(f"swapped_{i}", cat="Binary") for i in range(half)]
    for i in range(1, half):
        problem += swapped[i] <= swapped[i - 1]
    for i in range(half):
        x, y = 2 * i, 2 * i + 1
        problem += put[x][x][y] == swapped[i]
        problem += put[y][y][x] == swapped[i]
        problem += put[x][x][x] == 1 - swapped[i]
        problem += put[y][y][y] == 1 - swapped[i]
    if m % 2 == 1:
        problem += put[m - 1][m - 1][m - 1] == 1

    return problem, {"quasigroup": quasigroup}
