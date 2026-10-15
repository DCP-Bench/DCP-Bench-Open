# Periodic binary autocorrelation: choose a +1/-1 sequence of length n that minimises the sum of squared periodic autocorrelations E = sum_{k=1}^{n-1} C_k^2.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    m = Model()

    # bit b[i] = 1 means the sequence entry S_i is +1, and 0 means -1 (S_i = 2 b[i] - 1)
    b = [m.addVar(name=f"b_{i}", vtype="B") for i in range(n)]
    s = [2 * b[i] - 1 for i in range(n)]

    # x[i, j] = 1 when S_i and S_j differ, so S_i * S_j = 1 - 2 x[i, j]
    pair = {}

    def differ(i, j):
        key = (min(i, j), max(i, j))
        if key not in pair:
            x = m.addVar(name=f"x_{key[0]}_{key[1]}", vtype="B")
            # x = b_i XOR b_j (the three binaries sum to an even number)
            m.addConsXor([b[key[0]], b[key[1]], x], False)
            pair[key] = x
        return pair[key]

    # C[k] is the k-th periodic autocorrelation: sum_i S_i * S_{(i+k) mod n}
    C = {}
    # z[k] stands for C_k^2 and is minimised
    z = {}
    for k in range(1, n):
        # the products S_i * S_{(i+k) mod n} for every shift i, each written as 1 - 2 x
        # periodic: the sum has n terms, each -1 or +1
        C[k] = m.addVar(name=f"C_{k}", vtype="I", lb=-n, ub=n)
        m.addCons(C[k] == quicksum(1 - 2 * differ(i, (i + k) % n) for i in range(n)))
        z[k] = m.addVar(name=f"z_{k}", vtype="C", lb=0, ub=n * n)
        # z_k >= C_k^2, so minimising the sum of z_k minimises the energy
        m.addCons(z[k] >= C[k] ** 2)

    # the objective is the energy E = sum_k C_k^2
    m.setObjective(quicksum(z[k] for k in range(1, n)), "minimize")

    # the output gives the sequence as +1/-1 integers
    return m, {"sequence": s}
