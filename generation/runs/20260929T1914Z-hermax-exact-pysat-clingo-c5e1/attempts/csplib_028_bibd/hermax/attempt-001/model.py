# Balanced incomplete block design: arrange v objects into b blocks so that a
# block holds k objects, an object lies in r blocks, and any two distinct
# objects share exactly l blocks. Solved through the v x b incidence matrix.
from hermax.model import Model


def build(instance):
    v, b, r, k, l = instance["v"], instance["b"], instance["r"], instance["k"], instance["l"]

    m = Model()
    # matrix[i][j] is true when object i belongs to block j
    matrix = m.bool_matrix("matrix", v, b)

    # every object occurs in exactly r blocks (each row adds up to r)
    for i in range(v):
        m &= (sum(1 * matrix[i][j] for j in range(b)) == r)
    # every block contains exactly k objects (each column adds up to k)
    for j in range(b):
        m &= (sum(1 * matrix[i][j] for i in range(v)) == k)

    # any two distinct objects occur together in exactly l blocks: the scalar
    # product of their rows is l. both[j] is true when both objects are in block j.
    for i1 in range(v):
        for i2 in range(i1 + 1, v):
            together = []
            for j in range(b):
                both = m.bool(f"both_{i1}_{i2}_{j}")
                m &= (~both | matrix[i1][j])
                m &= (~both | matrix[i2][j])
                m &= (both | ~matrix[i1][j] | ~matrix[i2][j])
                together.append(both)
            m &= (sum(1 * lit for lit in together) == l)

    return m, {"matrix": matrix}
