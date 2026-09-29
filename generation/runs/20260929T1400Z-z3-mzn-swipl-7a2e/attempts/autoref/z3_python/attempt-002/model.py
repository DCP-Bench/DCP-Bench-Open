# Autoref: find a series s[0..n+1] in which every i from 0 to n occurs exactly
# s[i] times, and whose last element s[n+1] equals m.
import z3


def build(instance):
    n = instance["n"]
    m = instance["m"]  # required value of the last element

    solver = z3.Solver()

    # the series has n + 2 positions; every value lies between 0 and n
    s = [z3.Int(f"s_{k}") for k in range(n + 2)]
    for k in range(n + 2):
        solver.add(s[k] >= 0, s[k] <= n)

    # the last element is m
    solver.add(s[n + 1] == m)

    # the value i occurs exactly s[i] times in the series (Z3 has no counting
    # constraint, so each position contributes 1 if it holds i and 0 otherwise)
    for i in range(n + 1):
        solver.add(z3.Sum([z3.If(s[k] == i, 1, 0) for k in range(n + 2)]) == s[i])

    # Two consequences of the counting rule that the solver cannot derive by
    # itself, stated to prune the search (they remove no solution). The counts
    # s[0..n] together account for every position, so they add up to n + 2; and
    # counting the values of the series by value or by position gives the same
    # total, sum_i i * s[i] = sum_k s[k].
    solver.add(z3.Sum(s[: n + 1]) == n + 2)
    solver.add(z3.Sum([i * s[i] for i in range(n + 1)]) == z3.Sum(s))

    return solver, {"s": s}
