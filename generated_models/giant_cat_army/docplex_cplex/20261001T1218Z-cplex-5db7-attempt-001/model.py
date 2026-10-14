"""Giant cat army riddle: starting from [0], extend a list by adding 5, adding 7 or taking a
square root, keeping all numbers distinct integers of at most 60, so that 2, 10 and 14 appear
in that order; the list has 24 numbers and ends with 14.
"""
import math

from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data; the length, the bound and the targets are from the
    # statement.
    maxval = 60
    n = 24
    steps = range(n - 1)

    model = Model("giant_cat_army")

    # x[i] is the i-th number of the list. It starts with 0 and ends with 14.
    x = [model.integer_var(0, maxval, name=f"x_{i}") for i in range(n)]
    model.add_constraint(x[0] == 0)
    model.add_constraint(x[n - 1] == 14)

    # All numbers are different. Pairwise "different" is the smallest encoding here: one-hot
    # values would need 24 x 61 binaries, beyond the Community Edition's 1000 variables.
    for i in range(n):
        for j in range(i + 1, n):
            model.add(x[i] != x[j])

    # Each step adds 5, adds 7, or takes a square root (x[i] == x[i+1] * x[i+1]). A square
    # root step from r * r to r is one of the roots r with r * r <= 60; roots 0 and 1 would
    # repeat a number, which the distinctness above forbids, so they are left out.
    roots = [r for r in range(2, math.isqrt(maxval) + 1)]
    for i in steps:
        add5 = model.binary_var(name=f"add5_{i}")
        add7 = model.binary_var(name=f"add7_{i}")
        root = {r: model.binary_var(name=f"root_{i}_{r}") for r in roots}
        model.add_constraint(add5 + add7 + model.sum(root.values()) == 1)
        # The next number follows from the chosen step ...
        model.add_constraint(x[i + 1] - x[i]
                             == 5 * add5 + 7 * add7 + model.sum((r - r * r) * b
                                                                 for r, b in root.items()))
        # ... and a square root step starts from the square r * r.
        for r, b in root.items():
            model.add_indicator(b, x[i] == r * r)
        if i == 0:
            # The second number is 5 or 7.
            model.add_constraint(add5 + add7 == 1)

    # 2 appears at some position ix2 >= 1 and 10 at a later position ix10.
    later = range(1, n)
    is2 = {i: model.binary_var(name=f"is2_at_{i}") for i in later}
    is10 = {i: model.binary_var(name=f"is10_at_{i}") for i in later}
    for i in later:
        model.add_indicator(is2[i], x[i] == 2)
        model.add_indicator(is10[i], x[i] == 10)
    model.add_constraint(model.sum(is2.values()) == 1)
    model.add_constraint(model.sum(is10.values()) == 1)
    model.add_constraint(model.sum(i * b for i, b in is2.items()) + 1
                         <= model.sum(i * b for i, b in is10.items()))

    return model, {"x": x}
