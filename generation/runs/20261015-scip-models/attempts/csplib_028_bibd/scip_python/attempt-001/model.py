# BIBD: find a v-by-b binary incidence matrix with r ones per row, k ones per column, and scalar product lambda between every pair of distinct rows.
from pyscipopt import Model, quicksum


def build(instance):
    v = instance["v"]  # number of objects (rows)
    b = instance["b"]  # number of blocks (columns)
    r = instance["r"]  # each object occurs in r blocks
    k = instance["k"]  # each block contains k objects
    lam = instance["l"]  # every two distinct objects occur together in lambda blocks

    m = Model()

    # x[i, j] = 1 if object i is in block j
    x = {(i, j): m.addVar(name=f"x_{i}_{j}", vtype="B") for i in range(v) for j in range(b)}

    # each object occurs in exactly r blocks
    for i in range(v):
        m.addCons(quicksum(x[i, j] for j in range(b)) == r)

    # each block contains exactly k distinct objects
    for j in range(b):
        m.addCons(quicksum(x[i, j] for i in range(v)) == k)

    # every two distinct objects occur together in exactly lambda blocks
    # (the scalar product of each pair of distinct rows equals lambda)
    # y[i, i2, j] = 1 if objects i and i2 both occur in block j
    for i in range(v):
        for i2 in range(i + 1, v):
            y = {}
            for j in range(b):
                y[j] = m.addVar(name=f"y_{i}_{i2}_{j}", vtype="B")
                m.addConsAnd([x[i, j], x[i2, j]], y[j])
            m.addCons(quicksum(y[j] for j in range(b)) == lam)

    # output: the incidence matrix as 0/1 integers
    matrix = [[x[i, j] for j in range(b)] for i in range(v)]
    return m, {"matrix": matrix}
