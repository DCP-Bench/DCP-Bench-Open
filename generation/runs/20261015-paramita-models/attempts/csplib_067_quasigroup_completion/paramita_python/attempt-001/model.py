"""Quasigroup completion (order N Latin square with some cells given).

Each cell holds one value from 1..N. Every row and every column contains each
value exactly once. Given cells keep their value; 0 marks an empty cell.
The output puzzle is the completed square, values 1..N.
"""
from paramita.modelling import Bool


def build(instance):
    n = instance["N"]
    start = instance["start"]
    rng = range(n)

    # x[r][c][v] = 1 if cell (r, c) holds value v+1 (one-hot encoding of the cell)
    x = [[[Bool(f"x_{r}_{c}_{v}") for v in rng] for c in rng] for r in rng]

    cons = []

    # each cell holds exactly one value
    for r in rng:
        for c in rng:
            cons.append(sum(x[r][c]) == 1)

    # each row contains each value exactly once
    for r in rng:
        for v in rng:
            cons.append(sum(x[r][c][v] for c in rng) == 1)

    # each column contains each value exactly once
    for c in rng:
        for v in rng:
            cons.append(sum(x[r][c][v] for r in rng) == 1)

    # the given cells keep their value (0 marks an empty cell)
    for r in rng:
        for c in rng:
            g = start[r][c]
            if g != 0:
                cons.append(x[r][c][g - 1] == 1)

    # the completed square: value of each cell
    puzzle = [[sum((v + 1) * x[r][c][v] for v in rng) for c in rng] for r in rng]

    return cons, {"puzzle": puzzle}
