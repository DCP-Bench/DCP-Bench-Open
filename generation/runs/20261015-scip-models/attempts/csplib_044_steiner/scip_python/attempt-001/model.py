# Ternary Steiner system of order n: a family of n(n-1)/6 triples over {0..n-1} such that every pair
# of distinct elements lies in exactly one triple (so any two triples share at most one element).
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    num_triples = n * (n - 1) // 6  # n mod 6 must be 1 or 3 for this to be an integer
    m = Model()

    # x[t, e] = 1 if element e is part of triple t
    x = {(t, e): m.addVar(name=f"x_{t}_{e}", vtype="B") for t in range(num_triples) for e in range(n)}

    # each triple consists of exactly three distinct elements
    for t in range(num_triples):
        m.addCons(quicksum(x[t, e] for e in range(n)) == 3, name=f"triple_size_{t}")

    # every pair of distinct elements is covered by exactly one triple:
    # y[t, i, j] = 1 iff both i and j are in triple t
    # (this also gives: any two triples have at most one common element)
    for i in range(n):
        for j in range(i + 1, n):
            ys = []
            for t in range(num_triples):
                y = m.addVar(name=f"y_{t}_{i}_{j}", vtype="B")
                m.addConsAnd([x[t, i], x[t, j]], y)
                ys.append(y)
            m.addCons(quicksum(ys) == 1, name=f"pair_once_{i}_{j}")

    # the output is the triple-by-element boolean matrix
    sets = [[x[t, e] for e in range(n)] for t in range(num_triples)]
    return m, {"sets": sets}
