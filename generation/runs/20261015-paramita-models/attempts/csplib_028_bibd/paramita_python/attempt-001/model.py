# Balanced incomplete block design (BIBD) with parameters (v, b, r, k, lambda).
# The incidence matrix is v by b with 0/1 entries: each object (row) occurs in
# exactly r blocks, each block (column) holds exactly k objects, and every two
# distinct objects occur together in exactly lambda blocks.
#
# Encoding: one Bool per matrix cell X[i][j]. The auxiliary P[i][i2][j] says
# that cell (i, j) and cell (i2, j) are both 1, so the scalar product of two
# rows is the sum of their P values.

from paramita.modelling import Bool, Iff


def build(instance):
    v, b = instance["v"], instance["b"]
    r, k, lam = instance["r"], instance["k"], instance["l"]

    X = [[Bool(f"x_{i}_{j}") for j in range(b)] for i in range(v)]

    cons = []

    # each object occurs in exactly r blocks: r ones per row
    for i in range(v):
        cons.append(sum(X[i]) == r)

    # each block holds exactly k objects: k ones per column
    for j in range(b):
        cons.append(sum(X[i][j] for i in range(v)) == k)

    # every two distinct objects occur together in exactly lambda blocks:
    # the scalar product of any two distinct rows is lambda
    for i in range(v):
        for i2 in range(i + 1, v):
            both = []
            for j in range(b):
                p = Bool(f"both_{i}_{i2}_{j}")
                cons.append(Iff(p, X[i][j] & X[i2][j]))
                both.append(p)
            cons.append(sum(both) == lam)

    return cons, {"matrix": X}
