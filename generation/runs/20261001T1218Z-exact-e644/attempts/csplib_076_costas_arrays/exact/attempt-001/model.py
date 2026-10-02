# Costas arrays: place n marks on an n x n grid, one per row and one per column, so that the
# n(n-1)/2 vectors between pairs of marks are all different.
from exact import Exact


def build(instance):
    n = instance["n"]

    solver = Exact()

    # costas[i] is the column (1..n) of the mark in row i
    costas = [f"costas_{i}" for i in range(n)]
    for name in costas:
        solver.addVariable(name, 1, n)

    # at[i][v] = 1 when costas[i] == v. The columns form a permutation of 1..n; Exact has no
    # all-different constraint, so it is posted through these indicators: one value per row and
    # at most (here exactly) one row per value.
    at = [[f"row_{i}_at_{v}" for v in range(1, n + 1)] for i in range(n)]
    for i in range(n):
        for name in at[i]:
            solver.addVariable(name, 0, 1)
        solver.addConstraint([(1, name) for name in at[i]], True, 1, True, 1)
        solver.addConstraint([(v, at[i][v - 1]) for v in range(1, n + 1)] + [(-1, costas[i])],
                             True, 0, True, 0)
    for v in range(n):
        solver.addConstraint([(1, at[i][v]) for i in range(n)], True, 1, True, 1)

    # For each distance l, the differences costas[i + l] - costas[i] of the pairs of marks l rows
    # apart must all be different. diff_is[l][i][d] = 1 when that difference equals d, and each
    # difference value d is taken by at most one pair. The difference lies in -(n-1)..(n-1).
    for l in range(1, n - 1):  # distance n-1 has a single pair, so nothing to compare
        pairs = n - l
        diff_is = [[f"diff_{l}_{i}_is_{d}" for d in range(-(n - 1), n)] for i in range(pairs)]
        for i in range(pairs):
            for name in diff_is[i]:
                solver.addVariable(name, 0, 1)
            # each pair has exactly one difference value, and the value matches the two marks
            solver.addConstraint([(1, name) for name in diff_is[i]], True, 1, True, 1)
            solver.addConstraint([(d, diff_is[i][d + n - 1]) for d in range(-(n - 1), n) if d != 0]
                                 + [(-1, costas[i + l]), (1, costas[i])], True, 0, True, 0)
        # no difference value is used by two pairs at this distance
        for d in range(-(n - 1), n):
            solver.addConstraint([(1, diff_is[i][d + n - 1]) for i in range(pairs)], False, 0, True, 1)

    return solver, {"costas": costas}
