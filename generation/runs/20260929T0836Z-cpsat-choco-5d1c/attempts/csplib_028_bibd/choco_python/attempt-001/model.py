# Balanced incomplete block design: arrange v objects into b blocks so that a
# block holds k objects, an object lies in r blocks, and any two distinct
# objects share exactly l blocks. Solved through the v x b incidence matrix.
from pychoco.model import Model


def build(instance):
    v, b, r, k, l = instance["v"], instance["b"], instance["r"], instance["k"], instance["l"]

    model = Model()

    # matrix[i][j] is true when object i belongs to block j
    matrix = [[model.boolvar(name=f"matrix_{i}_{j}") for j in range(b)] for i in range(v)]

    # every object occurs in exactly r blocks (each row adds up to r)
    for i in range(v):
        model.sum(matrix[i], "=", r).post()

    # every block contains exactly k objects (each column adds up to k)
    for j in range(b):
        model.sum([matrix[i][j] for i in range(v)], "=", k).post()

    # any two distinct objects occur together in exactly l blocks: the scalar
    # product of their rows is l. both[j] is the product of the two entries in
    # block j, so the products are summed instead of multiplying inside a sum.
    for i1 in range(v):
        for i2 in range(i1 + 1, v):
            together = []
            for j in range(b):
                both = model.boolvar(name=f"both_{i1}_{i2}_{j}")
                model.times(matrix[i1][j], matrix[i2][j], both).post()
                together.append(both)
            model.sum(together, "=", l).post()

    return model, {"matrix": matrix}
