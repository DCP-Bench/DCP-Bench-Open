# Place n queens so that no two share a row, column or diagonal.
# Columns are 1-indexed, as the reference declares them.
from exact import Exact


def indicators(solver, name, lo, hi):
    """0/1 variables, one per value, with y[v] == 1 exactly when name == v."""
    flags = {v: f"{name}_is_{v}" for v in range(lo, hi + 1)}
    for flag in flags.values():
        solver.addVariable(flag, 0, 1)
    solver.addConstraint([(1, f) for f in flags.values()], True, 1, True, 1)
    solver.addConstraint([(v, flags[v]) for v in flags] + [(-1, name)],
                         True, 0, True, 0)
    return flags



def build(instance):
    n = instance["n"]

    solver = Exact()
    queens = [f"q{i}" for i in range(n)]
    for name in queens:
        solver.addVariable(name, 1, n)
    flags = {name: indicators(solver, name, 1, n) for name in queens}

    # All three all-differents go through the same indicators: no column and no
    # diagonal holds two queens.
    for value in range(1, n + 1):
        solver.addConstraint([(1, flags[name][value]) for name in queens],
                             False, 0, True, 1)
    for i in range(n):
        for j in range(i + 1, n):
            for v in range(1, n + 1):
                for w in (v + (j - i), v - (j - i)):
                    if 1 <= w <= n:
                        solver.addConstraint(
                            [(1, flags[queens[i]][v]), (1, flags[queens[j]][w])],
                            False, 0, True, 1)
    return solver, {"queens": queens}
