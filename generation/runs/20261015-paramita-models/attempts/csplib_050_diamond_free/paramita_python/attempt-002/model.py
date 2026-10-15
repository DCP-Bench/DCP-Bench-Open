# Diamond-free degree sequence: find a simple graph on N vertices whose degrees
# are positive multiples of 3, whose degree sum is a multiple of 12, with
# d_i >= d_{i+1}, and which has no diamond (no 4 vertices with 5 or more edges
# between them). N is read from the instance.
# Encoding: one Bool per vertex pair (edge). Degrees are sums of edge Bools.
# Multiples of 3 and 12 use unary counters (q >= 1 gives positive degree).
from paramita.modelling import Bool, If
from itertools import combinations


def unary(prefix, k_max):
    # bits[k] is true when the counter is at least k + 1
    bits = [Bool(f"{prefix}_ge_{k}") for k in range(1, k_max + 1)]
    cons = [If(bits[k], bits[k - 1]) for k in range(1, len(bits))]
    return bits, cons


def build(instance):
    n = instance["N"]
    verts = range(n)
    cons = []

    # one Bool per unordered pair; the matrix is symmetric, diagonal is empty
    edge = {}
    for u, v in combinations(verts, 2):
        edge[(u, v)] = Bool(f"e_{u}_{v}")
        edge[(v, u)] = edge[(u, v)]
    matrix = [[None] * n for _ in verts]
    for u in verts:
        for v in verts:
            if u == v:
                diag = Bool(f"loop_{u}")
                cons.append(~diag)  # no loop edges
                matrix[u][v] = diag
            else:
                matrix[u][v] = edge[(u, v)]

    deg = {v: sum(matrix[v][u] for u in verts if u != v) for v in verts}

    # each degree is greater than zero and divisible by 3: deg_v = 3 * q_v, q_v >= 1
    for v in verts:
        q_bits, q_cons = unary(f"q_{v}", (n - 1) // 3)
        cons += q_cons
        cons.append(deg[v] == 3 * sum(q_bits) if q_bits else deg[v] == 0)
        if q_bits:
            cons.append(q_bits[0])

    # degrees in non-increasing order: d_i >= d_{i+1}
    for v in range(n - 1):
        cons.append(deg[v] >= deg[v + 1])

    # sum of the degrees is a multiple of 12 (so |E| is a multiple of 6): sum = 12 * t
    total = sum(deg.values())
    t_bits, t_cons = unary("t", n * (n - 1) // 12)
    cons += t_cons
    cons.append(total == 12 * sum(t_bits) if t_bits else total == 0)

    # diamond-free: every set of four vertices has at most four edges between them
    for quad in combinations(verts, 4):
        pairs = [edge[(a, b)] for a, b in combinations(quad, 2)]
        cons.append(sum(pairs) <= 4)

    return cons, {"matrix": matrix}
