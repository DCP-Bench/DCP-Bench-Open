"""Costas array: a permutation costas of 1..n such that, for every distance d, the differences
costas[j + d] - costas[j] over all positions j are all different (each row of the difference
triangle holds different values).

The model reports the permutation.
"""
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]  # size of the Costas array

    positions = range(n)
    values = range(1, n + 1)

    model = Model("costas_array")
    # The difference rule below is a quadratic constraint over binaries, which is not convex.
    # CPLEX refuses such a constraint unless it is told to search for a global optimum.
    model.parameters.optimalitytarget = 3
    # There is no objective, only a solution to find: tell CPLEX to favour finding one.
    model.parameters.emphasis.mip = 1

    # at[j, v] is 1 when position j holds the value v. The values are all different: each
    # position holds one value and each value is used once.
    at = {(j, v): model.binary_var(name=f"at_{j}_{v}") for j in positions for v in values}
    for j in positions:
        model.add_constraint(model.sum(at[j, v] for v in values) == 1)
    for v in values:
        model.add_constraint(model.sum(at[j, v] for j in positions) == 1)

    # costas[j] is the value at position j.
    costas = [model.sum(v * at[j, v] for v in values) for j in positions]

    # All entries in a row of the difference triangle are distinct. Row d - 1 holds the
    # differences costas[j + d] - costas[j]; the reference constrains the rows of distances
    # 1..n-2 (the last row has a single entry). A difference equal to delta between positions
    # j and j + d means position j holds some v and position j + d holds v + delta, so for
    # each distance and each delta at most one such pair of positions may exist. The
    # difference 0 never occurs, as the values are all different.
    for d in range(1, n - 1):
        for delta in range(-(n - 1), n):
            if delta == 0:
                continue
            pairs = [(j, v) for j in range(n - d) for v in values if 1 <= v + delta <= n]
            model.add_constraint(
                model.sum(at[j, v] * at[j + d, v + delta] for j, v in pairs) <= 1)

    return model, {"costas": costas}
