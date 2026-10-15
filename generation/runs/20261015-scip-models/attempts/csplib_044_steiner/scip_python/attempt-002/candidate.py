# Ternary Steiner system of order n: a set of n(n-1)/6 triples of elements of
# {1, ..., n} such that any two triples have at most one common element.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    num_triples = n * (n - 1) // 6  # number of triples in a Steiner triple system of order n
    m = Model()

    # x[t, e] = 1 if element e belongs to triple t
    x = {(t, e): m.addVar(name=f"x[{t},{e}]", vtype="B") for t in range(num_triples) for e in range(n)}

    # each triple consists of three distinct elements
    for t in range(num_triples):
        # a triple has exactly three elements
        m.addCons(quicksum(x[t, e] for e in range(n)) == 3)

    # any two triples share at most one element: every pair of elements lies in at most one triple
    for a in range(n):
        for b in range(a + 1, n):
            # r[t, a, b] = 1 if triple t contains both elements a and b
            r = []
            for t in range(num_triples):
                rv = m.addVar(name=f"pair[{t},{a},{b}]", vtype="B")
                m.addConsAnd([x[t, a], x[t, b]], rv)
                r.append(rv)
            # the pair {a, b} is covered by at most one triple
            m.addCons(quicksum(r) <= 1)

    # each element lies in (n - 1) / 2 triples, since its n - 1 pairs are each covered once
    for e in range(n):
        m.addCons(quicksum(x[t, e] for t in range(num_triples)) == (n - 1) // 2)

    # the objective is only to find a feasible set of triples
    m.setObjective(0, "minimize")

    # sets[t][e] = true if element e is part of triple t
    sets = [[x[t, e] for e in range(n)] for t in range(num_triples)]
    return m, {"sets": sets}
