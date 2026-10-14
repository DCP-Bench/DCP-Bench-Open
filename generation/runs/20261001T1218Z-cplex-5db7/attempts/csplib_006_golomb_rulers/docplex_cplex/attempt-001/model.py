"""Golomb ruler: place `size` marks at integer positions 0 = a_1 < a_2 < ... < a_m so that the
m(m-1)/2 differences a_j - a_i (i < j) are all different, with the ruler as short as possible.

The model reports the positions of the marks and the length of the ruler (the last mark).
"""
from docplex.mp.model import Model


def build(instance):
    size = instance["size"]  # number of marks
    # The reference lets every mark lie between 0 and size * size; the model keeps that range.
    horizon = size * size

    model = Model("golomb_ruler")
    # "At most one pair of marks at each distance" is a quadratic constraint over binaries,
    # which is not convex. CPLEX refuses such a constraint unless it is told to search for a
    # global optimum.
    model.parameters.optimalitytarget = 3

    # Mark i is preceded by i marks and followed by size - 1 - i, all at different places, and
    # the gaps between neighbouring marks are different positive whole numbers: the i gaps up to
    # mark i add up to at least 1 + 2 + ... + i, and the size - 1 - i gaps after it to at least
    # 1 + 2 + ... + (size - 1 - i). So mark i lies between low[i] and high[i]. The first mark
    # is at 0.
    low = [i * (i + 1) // 2 for i in range(size)]
    high = [horizon - (size - 1 - i) * (size - i) // 2 for i in range(size)]
    high[0] = 0

    # at[i, p] is 1 when mark i is at position p.
    at = {(i, p): model.binary_var(name=f"at_{i}_{p}")
          for i in range(size) for p in range(low[i], high[i] + 1)}

    # Every mark has exactly one position.
    for i in range(size):
        model.add_constraint(model.sum(at[i, p] for p in range(low[i], high[i] + 1)) == 1)

    # marks[i] is the position of mark i (declared output); length is the position of the
    # last mark (declared output).
    marks = [model.sum(p * at[i, p] for p in range(low[i], high[i] + 1)) for i in range(size)]
    length = marks[size - 1]

    # The marks are increasing along the ruler.
    for i in range(size - 1):
        model.add_constraint(marks[i] + 1 <= marks[i + 1])

    # used[p] is 1 when some mark is at position p.
    used = [model.binary_var(name=f"used_{p}") for p in range(horizon + 1)]
    for p in range(horizon + 1):
        model.add_constraint(
            used[p] == model.sum(at[i, p] for i in range(size) if (i, p) in at))

    # The differences are all different: for each distance d, at most one pair of used
    # positions p and p + d. The marks are written once as positions, rather than one
    # difference variable per pair of marks and value, to stay inside the Community Edition's
    # 1000 variables.
    for d in range(1, horizon + 1):
        pairs = model.sum(used[p] * used[p + d] for p in range(horizon + 1 - d))
        model.add_constraint(pairs <= 1)

    # Objective: the shortest ruler.
    model.minimize(length)

    return model, {"marks": marks, "length": length}
