# QG3 quasigroup existence: find an order m quasigroup (Latin square) q with
# (a*b)*(b*a) = a for all a, b, where a*b = q[a][b].
from pyscipopt import Model, quicksum


def build(instance):
    m_order = instance["m"]  # order of the quasigroup
    rng = range(m_order)

    m = Model()

    # x[i,j,v] = 1 if the table entry q[i][j] equals v
    x = {(i, j, v): m.addVar(name=f"x_{i}_{j}_{v}", vtype="B")
         for i in rng for j in rng for v in rng}

    # each cell of the multiplication table holds exactly one value
    for i in rng:
        for j in rng:
            # every cell a*b has exactly one value
            m.addCons(quicksum(x[i, j, v] for v in rng) == 1)

    # each element occurs once in every row and column
    for i in rng:
        for v in rng:
            # every row contains each value once
            m.addCons(quicksum(x[i, j, v] for j in rng) == 1)
    for j in rng:
        for v in rng:
            # every column contains each value once
            m.addCons(quicksum(x[i, j, v] for i in rng) == 1)

    # QG3 identity: (a*b)*(b*a) = a
    # With c = a*b and d = b*a, the entry c*d must equal a. If q[a][b] = c and
    # q[b][a] = d, then x[c,d,a] must be 1.
    for a in rng:
        for b in rng:
            # (a*b)*(b*a) = a
            for c in rng:
                for d in rng:
                    m.addCons(x[a, b, c] + x[b, a, d] - 1 <= x[c, d, a])

    quasigroup = [[quicksum(v * x[i, j, v] for v in rng) for j in rng] for i in rng]
    return m, {"quasigroup": quasigroup}
