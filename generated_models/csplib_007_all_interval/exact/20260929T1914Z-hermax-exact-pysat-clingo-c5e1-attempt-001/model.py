# All-interval series: a permutation of the pitch classes 0..n-1 whose
# successive absolute differences are themselves all distinct.
from exact import Exact


def build(instance):
    n = instance["n"]

    solver = Exact()
    x = [f"x_{i}" for i in range(n)]
    diffs = [f"diff_{i}" for i in range(n - 1)]
    # x_is[i][a] is 1 when the i-th pitch class is a; diff_is[i][d] when the i-th interval is d
    x_is = [{} for _ in range(n)]
    diff_is = [{} for _ in range(n - 1)]
    for i in range(n):
        solver.addVariable(x[i], 0, n - 1)
        for a in range(n):
            x_is[i][a] = f"x_{i}_is_{a}"
            solver.addVariable(x_is[i][a], 0, 1)
        solver.addConstraint([(1, x_is[i][a]) for a in range(n)], True, 1, True, 1)
        solver.addConstraint([(a, x_is[i][a]) for a in range(1, n)] + [(-1, x[i])], True, 0, True, 0)
    for i in range(n - 1):
        solver.addVariable(diffs[i], 1, n - 1)
        for d in range(1, n):
            diff_is[i][d] = f"diff_{i}_is_{d}"
            solver.addVariable(diff_is[i][d], 0, 1)
        solver.addConstraint([(1, diff_is[i][d]) for d in range(1, n)], True, 1, True, 1)
        solver.addConstraint([(d, diff_is[i][d]) for d in range(1, n)] + [(-1, diffs[i])], True, 0, True, 0)

    # the pitch classes are a permutation, and all intervals differ
    for a in range(n):
        solver.addConstraint([(1, x_is[i][a]) for i in range(n)], True, 1, True, 1)
    for d in range(1, n):
        solver.addConstraint([(1, diff_is[i][d]) for i in range(n - 1)], False, 0, True, 1)

    # each interval is the absolute difference of its two pitch classes: for every
    # pair of neighbouring values a != b the interval is |a - b|
    for i in range(n - 1):
        for a in range(n):
            for b in range(n):
                if a != b:
                    solver.addConstraint([(1, x_is[i][a]), (1, x_is[i + 1][b]), (-1, diff_is[i][abs(a - b)])],
                                         False, 0, True, 1)

    return solver, {"x": x, "diffs": diffs}
