"""Balanced incomplete block design (BIBD): a v-by-b 0/1 incidence matrix of objects and blocks
in which every object occurs in r blocks, every block holds k objects, and every pair of
distinct objects occurs together in exactly l blocks.

The model reports the incidence matrix.
"""
from docplex.mp.model import Model


def build(instance):
    v = instance["v"]  # number of distinct objects (rows)
    b = instance["b"]  # number of blocks (columns)
    r = instance["r"]  # number of blocks each object occurs in
    k = instance["k"]  # number of objects each block contains
    l = instance["l"]  # number of blocks each pair of distinct objects shares

    model = Model("bibd")
    # The pair rule is a quadratic constraint over binaries, which is not convex. CPLEX refuses
    # such a constraint unless it is told to search for a global optimum.
    model.parameters.optimalitytarget = 3

    # matrix[i][j] is 1 when object i occurs in block j.
    matrix = [[model.binary_var(name=f"matrix_{i}_{j}") for j in range(b)] for i in range(v)]

    # Every row adds up to r: each object occurs in r blocks.
    for i in range(v):
        model.add_constraint(model.sum(matrix[i]) == r)

    # Every column adds up to k: each block contains k objects.
    for j in range(b):
        model.add_constraint(model.sum(matrix[i][j] for i in range(v)) == k)

    # The scalar product of every pair of rows adds up to l: each pair of objects shares l
    # blocks. Only the "at most l" side is posted as a quadratic constraint. With every column
    # holding k objects, the scalar products of all pairs of rows add up to b * C(k, 2), a
    # fixed number; when that equals C(v, 2) * l, "at most l" for every pair forces "exactly
    # l". Otherwise the "at least l" side is posted too, so the model stays exact.
    pairs = [(i, h) for i in range(v) for h in range(i + 1, v)]
    for i, h in pairs:
        shared = model.sum(matrix[i][j] * matrix[h][j] for j in range(b))
        model.add_constraint(shared <= l)
    if b * k * (k - 1) // 2 != len(pairs) * l:
        for i, h in pairs:
            shared = model.sum(matrix[i][j] * matrix[h][j] for j in range(b))
            model.add_constraint(shared >= l)

    return model, {"matrix": matrix}
