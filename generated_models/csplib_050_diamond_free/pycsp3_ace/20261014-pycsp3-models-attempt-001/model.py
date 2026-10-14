# Problem: Find a diamond-free graph whose degree sequence meets the stated conditions and print its adjacency matrix.
from itertools import combinations
from pycsp3 import *

N = data.N
# matrix[i][j] = 1 if vertices i and j are adjacent
matrix = VarArray(size=[N, N], dom={0, 1})
# deg[i] is the degree of vertex i: positive and divisible by 3
deg = VarArray(size=N, dom=list(range(3, N, 3)))
# total degree, the degree sum is divisible by 12
total = Var(dom=range(0, N * N))
satisfy(
    # no loop edges: a vertex is not adjacent to itself
    [matrix[i][i] == 0 for i in range(N)],
    # the graph is undirected
    [matrix[i][j] == matrix[j][i] for i in range(N) for j in range(i + 1, N)],
    # the degree of each vertex is the number of its edges
    [Sum(matrix[i]) == deg[i] for i in range(N)],
    # the degrees are in non-increasing order
    [deg[i] >= deg[i + 1] for i in range(N - 1)],
    # the sum of the degrees is divisible by 12
    Sum(deg) == 12 * total,
    # diamond-free: any four vertices have at most four edges between them
    [Sum(matrix[a][b] for a, b in combinations(q, 2)) <= 4 for q in combinations(range(N), 4)],
)
