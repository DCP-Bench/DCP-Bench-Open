# All-interval series problem (CSPLib 007) in cvc5 (pythonic API).
# Find a permutation x of 0..n-1 such that the absolute differences between
# neighbouring entries, diffs, are a permutation of 1..n-1.
# n is read from the instance.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]

    # x: the series, a permutation of 0..n-1 (declared shape [n])
    x = [cz.Int(f"x_{i}") for i in range(n)]
    # diffs: the interval vector, a permutation of 1..n-1 (declared shape [n-1])
    diffs = [cz.Int(f"d_{i}") for i in range(n - 1)]

    constraints = []

    # the series is a permutation of 0..n-1: each pitch-class occurs exactly once
    for xi in x:
        constraints.append(xi >= 0)
        constraints.append(xi <= n - 1)
    constraints.append(cz.Distinct(x))

    # the interval between neighbouring notes is the absolute difference of the two pitch-classes
    for i in range(n - 1):
        delta = x[i + 1] - x[i]
        # no Abs in cvc5 pythonic: |a| written as an If
        constraints.append(diffs[i] == cz.If(delta >= 0, delta, -delta))

    # the intervals cover the full set 1..n-1: each interval occurs exactly once
    for d in diffs:
        constraints.append(d >= 1)
        constraints.append(d <= n - 1)
    constraints.append(cz.Distinct(diffs))

    return constraints, {"x": x, "diffs": diffs}
