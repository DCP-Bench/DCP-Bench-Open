# Balanced incomplete block design: arrange v objects into b blocks so that a
# block holds k objects, an object lies in r blocks, and any two distinct
# objects share exactly l blocks. Solved through the v x b incidence matrix.
import z3


def build(instance):
    v, b, r, k, l = instance["v"], instance["b"], instance["r"], instance["k"], instance["l"]

    solver = z3.Solver()

    # matrix[i][j] is true when object i belongs to block j
    matrix = [[z3.Bool(f"matrix_{i}_{j}") for j in range(b)] for i in range(v)]

    # every object occurs in exactly r blocks (each row adds up to r)
    for i in range(v):
        solver.add(z3.PbEq([(matrix[i][j], 1) for j in range(b)], r))

    # every block contains exactly k objects (each column adds up to k)
    for j in range(b):
        solver.add(z3.PbEq([(matrix[i][j], 1) for i in range(v)], k))

    # any two distinct objects occur together in exactly l blocks: the scalar
    # product of their rows is l, that is, l blocks contain both objects
    for i1 in range(v):
        for i2 in range(i1 + 1, v):
            solver.add(z3.PbEq([(z3.And(matrix[i1][j], matrix[i2][j]), 1) for j in range(b)], l))

    return solver, {"matrix": matrix}
