"""Diamond-free graph: an undirected graph on N vertices with no vertex of degree 0, all degrees and the total degree divisible as required, and no four vertices spanning five or six edges."""
import gurobipy as gp
from gurobipy import GRB
from itertools import combinations


def build(instance):
    n = instance["N"]  # number of vertices
    vertices = range(n)

    model = gp.Model("diamond_free")

    # edge[i, j] (i < j) is 1 when vertices i and j are joined. The graph is undirected with
    # no loops, so one variable per pair stands for both matrix entries (i, j) and (j, i), and
    # the diagonal is 0. That settles the reference's symmetry and empty-diagonal constraints.
    edge = model.addVars(list(combinations(vertices, 2)), vtype=GRB.BINARY, name="edge")

    def joined(i, j):
        return edge[min(i, j), max(i, j)]

    # Degree of each vertex.
    degree = [gp.quicksum(joined(i, j) for j in vertices if j != i) for i in vertices]

    # No row of the matrix is all zeros: every vertex has at least one neighbour.
    for i in vertices:
        model.addConstr(degree[i] >= 1, name=f"has_neighbour[{i}]")

    # Every row sum is a multiple of 3: degree[i] = 3 * thirds[i].
    thirds = model.addVars(vertices, lb=0, ub=(n - 1) // 3, vtype=GRB.INTEGER, name="thirds")
    for i in vertices:
        model.addConstr(degree[i] == 3 * thirds[i], name=f"degree_mod3[{i}]")

    # The sum of the whole matrix (each edge counted twice) is a multiple of 12.
    twelfths = model.addVar(lb=0, ub=n * (n - 1) // 12, vtype=GRB.INTEGER, name="twelfths")
    model.addConstr(gp.quicksum(degree) == 12 * twelfths, name="total_mod12")

    # No diamond: any four vertices span at most 4 of their 6 possible edges.
    for a, b, c, d in combinations(vertices, 4):
        model.addConstr(joined(a, b) + joined(a, c) + joined(a, d) + joined(b, c) + joined(b, d)
                        + joined(c, d) <= 4, name=f"diamond[{a},{b},{c},{d}]")

    matrix = [[0 if i == j else joined(i, j) for j in vertices] for i in vertices]
    return model, {"matrix": matrix}
