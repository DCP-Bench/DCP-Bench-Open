# Hadamard matrix Legendre pairs: two +1/-1 sequences A, B of odd length l whose
# periodic autocorrelations sum to -2 at every shift s = 1..m, with m = (l-1)/2,
# and whose entries each sum to 1.
from pyscipopt import Model, quicksum


def build(instance):
    l = instance["l"]
    m = Model()
    mm = (l - 1) // 2

    # each entry is +1 or -1; p = 1 means +1 and p = 0 means -1, so value = 2p - 1
    pa = [m.addVar(name=f"pa_{i}", vtype="B") for i in range(l)]
    pb = [m.addVar(name=f"pb_{i}", vtype="B") for i in range(l)]
    a = [2 * pa[i] - 1 for i in range(l)]
    b = [2 * pb[i] - 1 for i in range(l)]

    # product variables: z[p, i, j] = p_i AND p_j, linearised with three inequalities
    zcache = {}

    def prod_var(p, i, j):
        key = (id(p), min(i, j), max(i, j))
        if key not in zcache:
            z = m.addVar(name=f"z_{len(zcache)}", vtype="B")
            m.addCons(z <= p[i])
            m.addCons(z <= p[j])
            m.addCons(z >= p[i] + p[j] - 1)
            zcache[key] = z
        return zcache[key]

    def product(p, i, j):
        # (2 p_i - 1)(2 p_j - 1) = 4 p_i p_j - 2 p_i - 2 p_j + 1
        z = prod_var(p, i, j)
        return 4 * z - 2 * p[i] - 2 * p[j] + 1

    # the entries of each sequence sum to 1
    # (sum of (2p - 1) = 1, i.e. sum of p = (l + 1) / 2)
    m.addCons(quicksum(pa) == (l + 1) // 2)
    m.addCons(quicksum(pb) == (l + 1) // 2)

    # periodic autocorrelation constraints: PAF(A, s) + PAF(B, s) = -2 for s = 1..m
    for s in range(1, mm + 1):
        # PAF(A, s) = sum over i of a_i a_{(i+s) mod l}
        paf_a = quicksum(product(pa, i, (i + s) % l) for i in range(l))
        # PAF(B, s) = sum over i of b_i b_{(i+s) mod l}
        paf_b = quicksum(product(pb, i, (i + s) % l) for i in range(l))
        # the two periodic autocorrelations sum to -2 at shift s
        m.addCons(paf_a + paf_b == -2)

    # the output gives the two sequences as lists of +1/-1 values
    return m, {"a": a, "b": b}
