# csplib 028: Balanced Incomplete Block Design (BIBD) with parameters (v, b, r, k, lambda).
# The incidence matrix has v rows (objects) and b columns (blocks), entries 0 or 1.
from cvc5.pythonic import And, Bool, If, Sum


def build(instance):
    v = instance["v"]
    b = instance["b"]
    r = instance["r"]
    k = instance["k"]
    lam = instance["l"]

    x = [[Bool(f"x_{i}_{c}") for c in range(b)] for i in range(v)]
    constraints = []

    # each object occurs in exactly r different blocks
    for i in range(v):
        constraints.append(Sum([If(x[i][c], 1, 0) for c in range(b)]) == r)

    # each block contains exactly k distinct objects
    for c in range(b):
        constraints.append(Sum([If(x[i][c], 1, 0) for i in range(v)]) == k)

    # every two distinct objects occur together in exactly lambda blocks
    for i in range(v):
        for j in range(i + 1, v):
            constraints.append(
                Sum([If(And(x[i][c], x[j][c]), 1, 0) for c in range(b)]) == lam
            )

    return constraints, {"matrix": x}
