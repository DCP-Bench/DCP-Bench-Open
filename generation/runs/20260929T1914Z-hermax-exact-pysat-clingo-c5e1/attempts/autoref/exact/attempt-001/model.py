# Autoref: find a series s[0..n+1] in which every i from 0 to n occurs exactly
# s[i] times, and whose last element s[n+1] equals m.
from exact import Exact


def build(instance):
    n = instance["n"]
    last_value = instance["m"]  # required value of the last element
    length = n + 2  # the series has n + 2 positions

    solver = Exact()
    # every value lies between 0 and n
    s = [f"s_{k}" for k in range(length)]
    # is_[k][v] is 1 exactly when position k holds v, so that "v occurs s[v]
    # times" is a linear count (n + 1 values for each of the n + 2 positions)
    is_ = [{} for _ in range(length)]
    for k in range(length):
        solver.addVariable(s[k], 0, n)
        for v in range(n + 1):
            is_[k][v] = f"is_{k}_{v}"
            solver.addVariable(is_[k][v], 0, 1)
        solver.addConstraint([(1, is_[k][v]) for v in range(n + 1)], True, 1, True, 1)
        solver.addConstraint([(v, is_[k][v]) for v in range(1, n + 1)] + [(-1, s[k])], True, 0, True, 0)

    # the last element is m
    solver.addConstraint([(1, s[n + 1])], True, last_value, True, last_value)

    # the value i occurs exactly s[i] times in the series
    for i in range(n + 1):
        solver.addConstraint([(1, is_[k][i]) for k in range(length)] + [(-1, s[i])], True, 0, True, 0)

    return solver, {"s": s}
