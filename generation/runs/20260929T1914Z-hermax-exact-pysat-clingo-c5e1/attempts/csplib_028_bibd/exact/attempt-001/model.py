# Balanced incomplete block design: arrange v objects into b blocks so that a
# block holds k objects, an object lies in r blocks, and any two distinct
# objects share exactly l blocks. Solved through the v x b incidence matrix.
from exact import Exact


def build(instance):
    v, b, r, k, l = instance["v"], instance["b"], instance["r"], instance["k"], instance["l"]

    solver = Exact()
    # matrix[i][j] is 1 when object i belongs to block j
    matrix = [[f"matrix_{i}_{j}" for j in range(b)] for i in range(v)]
    for row in matrix:
        for name in row:
            solver.addVariable(name, 0, 1)

    # every object occurs in exactly r blocks (each row adds up to r)
    for i in range(v):
        solver.addConstraint([(1, name) for name in matrix[i]], True, r, True, r)
    # every block contains exactly k objects (each column adds up to k)
    for j in range(b):
        solver.addConstraint([(1, matrix[i][j]) for i in range(v)], True, k, True, k)

    # any two distinct objects occur together in exactly l blocks: the scalar
    # product of their rows is l. both is 1 exactly when both objects are in block j.
    for i1 in range(v):
        for i2 in range(i1 + 1, v):
            together = []
            for j in range(b):
                both = f"both_{i1}_{i2}_{j}"
                solver.addVariable(both, 0, 1)
                solver.addConstraint([(1, both), (-1, matrix[i1][j])], False, 0, True, 0)
                solver.addConstraint([(1, both), (-1, matrix[i2][j])], False, 0, True, 0)
                solver.addConstraint([(1, both), (-1, matrix[i1][j]), (-1, matrix[i2][j])], True, -1)
                together.append((1, both))
            solver.addConstraint(together, True, l, True, l)

    return solver, {"matrix": matrix}
