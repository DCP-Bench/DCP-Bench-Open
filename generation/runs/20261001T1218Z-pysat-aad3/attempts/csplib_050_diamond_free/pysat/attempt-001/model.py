# Diamond-free graph: a simple undirected graph on N vertices, with no isolated vertex,
# every vertex degree a multiple of 3, the sum of the degrees a multiple of 12, and no
# four vertices spanning five or more edges (no diamond).
from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.pb import PBEnc


def build(instance):
    n = instance["N"]  # number of vertices

    pool = IDPool()
    cnf = CNF()
    # matrix[i][j] is true when vertices i and j are adjacent. The graph is undirected,
    # so matrix[j][i] is the very same literal as matrix[i][j].
    matrix = [[None] * n for _ in range(n)]
    for i, j in combinations(range(n), 2):
        matrix[i][j] = matrix[j][i] = pool.id(("edge", i, j))
    # a simple graph has no loops: the diagonal is false
    for i in range(n):
        matrix[i][i] = pool.id(("loop", i))
        cnf.append([-matrix[i][i]])

    def one_hot(key, count):
        """Selector literals s[1..count] of which exactly one is true."""
        selectors = [pool.id((key, v)) for v in range(1, count + 1)]
        cnf.extend(CardEnc.equals(lits=selectors, bound=1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
        return selectors

    # No vertex is isolated and every degree is a multiple of 3: the degree of vertex i
    # equals 3 * k_i for some k_i >= 1 (a degree is at most n - 1, so k_i <= (n - 1) // 3).
    # k_i is chosen one-hot, and PBEnc (which takes negative weights) equates
    # degree - 3 * k_i = 0.
    max_multiple = (n - 1) // 3
    for i in range(n):
        neighbours = [matrix[i][j] for j in range(n) if j != i]
        k = one_hot(("degree_multiple", i), max_multiple)
        cnf.extend(PBEnc.equals(lits=neighbours + k,
                                weights=[1] * len(neighbours) + [-3 * v for v in range(1, max_multiple + 1)],
                                bound=0, vpool=pool).clauses)

    # The sum of all matrix entries (twice the number of edges) is a multiple of 12, so
    # the number of edges is a multiple of 6: edges = 6 * t for some t >= 1.
    edges = [matrix[i][j] for i, j in combinations(range(n), 2)]
    max_t = len(edges) // 6
    t = one_hot("edge_multiple", max_t)
    cnf.extend(PBEnc.equals(lits=edges + t,
                            weights=[1] * len(edges) + [-6 * v for v in range(1, max_t + 1)],
                            bound=0, vpool=pool).clauses)

    # Diamond-free: every group of four vertices spans at most four of its six possible edges.
    for a, b, c, d in combinations(range(n), 4):
        group = [matrix[a][b], matrix[a][c], matrix[a][d],
                 matrix[b][c], matrix[b][d], matrix[c][d]]
        cnf.extend(CardEnc.atmost(lits=group, bound=4, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    return cnf, {"matrix": matrix}
