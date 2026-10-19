# csplib 050, diamond-free degree sequences, in Python-MIP with CBC.
# Output the adjacency matrix of a simple graph on N vertices. Its degree
# sequence d_1 >= ... >= d_N has each d_i > 0 and each d_i a multiple of 3,
# the sum of the degrees is a multiple of 12, and the graph is diamond-free.
import itertools

import mip


def build(instance):
    n = instance["N"]
    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Simple undirected graph: one binary per unordered pair, no loops.
    x = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            x[i][j] = m.add_var(f"x_{i}_{j}", var_type=mip.BINARY)
            x[j][i] = x[i][j]

    # Each degree d_i is positive and a multiple of 3: d_i = 3 * k_i with
    # 1 <= k_i and 3 * k_i <= n - 1.
    kmax = (n - 1) // 3
    k = [m.add_var(f"k_{i}", var_type=mip.INTEGER, lb=1, ub=kmax) for i in range(n)]
    for i in range(n):
        # d_i is the number of edges at vertex i
        m += mip.xsum(x[i][j] for j in range(n) if j != i) == 3 * k[i]

    # The degree sequence is listed in non-increasing order: d_i >= d_{i+1}.
    for i in range(n - 1):
        m += k[i] >= k[i + 1]

    # The sum of the degrees is a multiple of 12: sum d_i = 12 * t,
    # which is sum k_i = 4 * t, since d_i = 3 * k_i.
    t = m.add_var("t", var_type=mip.INTEGER, lb=0, ub=(n * kmax) // 4)
    m += mip.xsum(k) == 4 * t

    # Diamond-free: every set of four vertices spans at most four edges.
    for quad in itertools.combinations(range(n), 4):
        m += mip.xsum(x[a][b] for a, b in itertools.combinations(quad, 2)) <= 4

    matrix = [[False if i == j else x[i][j] for j in range(n)] for i in range(n)]
    return m, {"matrix": matrix}
