"""Costas array problem: n marks on an n x n grid, one mark per row and per
column, such that the differences between all pairs of marks are different.

Encoding: the mark in position i has value v in one-hot Bools xv[i][v].
Each difference X_i - X_{i+l} of difference-triangle line l is a one-hot
Bool over the difference value d, D[l][i][d]. Each line has all-different
differences."""

from paramita.modelling import Bool, If


def build(instance):
    n = instance["n"]
    vals = range(1, n + 1)
    pos = range(n)
    cons = []

    # Variables: xv[i][v] is true when position i holds the mark with value v.
    xv = [{v: Bool(f"x_{i}_{v}") for v in vals} for i in pos]

    # The values form a permutation: one value per position ...
    for i in pos:
        cons.append(sum(xv[i].values()) == 1)
    # ... and each value is used by exactly one position.
    for v in vals:
        cons.append(sum(xv[i][v] for i in pos) == 1)

    # Difference triangle: line l holds the differences X_i - X_{i+l}.
    # Each line must not contain any value twice (all-different per line).
    diffs = range(-(n - 1), n)
    for l in range(1, n):
        rows = []
        for i in range(n - l):
            j = i + l
            # D[d] is true exactly when X_i - X_j = d (d is a single difference value).
            D = {d: Bool(f"diff_{l}_{i}_{d + n}") for d in diffs}
            for u in vals:
                for w in vals:
                    cons.append(If(xv[i][u] & xv[j][w], D[u - w]))
            cons.append(sum(D.values()) == 1)
            rows.append(D)
        # Each difference value appears at most once in line l.
        for d in diffs:
            cons.append(sum(row[d] for row in rows) <= 1)

    # Output: the mark of each position as a 1-based integer.
    costas = [sum(v * xv[i][v] for v in vals) for i in pos]
    return cons, {"costas": costas}
