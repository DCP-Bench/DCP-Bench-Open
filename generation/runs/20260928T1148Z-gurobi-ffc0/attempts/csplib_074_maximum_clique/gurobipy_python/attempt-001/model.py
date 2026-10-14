"""Maximum clique: choose as many vertices as possible such that every two of them are adjacent."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n, adj = instance["n"], instance["adj"]
    vertices = range(n)

    model = gp.Model("maximum_clique")

    # c[i] is 1 when vertex i is in the clique.
    c = model.addVars(vertices, vtype=GRB.BINARY, name="c")

    # Two vertices that are not connected cannot both be in the clique.
    for i in vertices:
        for j in range(i + 1, n):
            if adj[i][j] == 0:
                model.addConstr(c[i] + c[j] <= 1, name=f"non_edge[{i},{j}]")

    # Maximise the size of the clique.
    model.setObjective(c.sum(), GRB.MAXIMIZE)

    return model, {"c": [c[i] for i in vertices]}
