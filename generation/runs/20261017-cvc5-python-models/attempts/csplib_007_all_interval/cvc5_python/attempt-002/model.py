# All-interval series problem (CSPLib 007) in cvc5 (pythonic API).
# Find a permutation x of 0..n-1 such that the absolute differences between
# neighbouring entries, diffs, are a permutation of 1..n-1.
# n is read from the instance. Linear integer logic (QF_LIA) is used.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]

    # x: the series, a permutation of 0..n-1 (declared shape [n])
    x = [cz.Int(f"x_{i}") for i in range(n)]
    # diffs: the interval vector, a permutation of 1..n-1 (declared shape [n-1])
    diffs = [cz.Int(f"d_{i}") for i in range(n - 1)]

    s = cz.SolverFor("QF_LIA")

    # the series is a permutation of 0..n-1: each pitch-class occurs exactly once
    for xi in x:
        s.add(xi >= 0, xi <= n - 1)
    s.add(cz.Distinct(x))

    # the interval between neighbouring notes is the absolute difference of the two pitch-classes:
    # diffs[i] equals x[i+1] - x[i] or x[i] - x[i+1], and is positive
    for i in range(n - 1):
        s.add(cz.Or(diffs[i] == x[i + 1] - x[i], diffs[i] == x[i] - x[i + 1]))
        s.add(diffs[i] >= 1, diffs[i] <= n - 1)

    # the intervals cover the full set 1..n-1: each interval occurs exactly once
    s.add(cz.Distinct(diffs))

    return s, {"x": x, "diffs": diffs}
