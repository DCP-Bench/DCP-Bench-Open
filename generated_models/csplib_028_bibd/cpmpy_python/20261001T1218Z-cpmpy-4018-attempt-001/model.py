# Balanced incomplete block design: arrange v objects into b blocks so that every block
# holds k objects, every object lies in r blocks, and every pair of distinct objects
# lies together in exactly l blocks. The answer is the v-by-b incidence matrix.
import cpmpy as cp


def build(instance):
    v = instance["v"]    # number of objects
    b = instance["b"]    # number of blocks
    r = instance["r"]    # number of blocks each object occurs in
    k = instance["k"]    # number of objects in each block
    l = instance["l"]    # number of blocks in which each pair of objects occurs together

    # matrix[i][j] is true when object i belongs to block j.
    matrix = cp.boolvar(shape=(v, b), name="matrix")

    model = cp.Model()

    # Every object occurs in exactly r blocks (each row sums to r).
    for i in range(v):
        model += cp.sum(matrix[i, :]) == r

    # Every block contains exactly k objects (each column sums to k).
    for j in range(b):
        model += cp.sum(matrix[:, j]) == k

    # Any two distinct objects occur together in exactly l blocks (the scalar product
    # of their rows is l).
    for i in range(v):
        for j in range(i + 1, v):
            model += cp.sum(matrix[i, :] * matrix[j, :]) == l

    return model, {"matrix": matrix}
