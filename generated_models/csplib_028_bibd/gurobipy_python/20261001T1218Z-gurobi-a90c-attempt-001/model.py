"""Balanced incomplete block design: a v-by-b incidence matrix of objects and blocks with r ones per row, k per column, and every two rows sharing exactly lambda blocks."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    v = instance["v"]  # number of objects (rows)
    b = instance["b"]  # number of blocks (columns)
    r = instance["r"]  # blocks each object occurs in
    k = instance["k"]  # objects each block contains
    lam = instance["l"]  # blocks shared by every two distinct objects

    model = gp.Model("bibd")

    # matrix[i, j] is 1 when object i is in block j.
    matrix = model.addVars(v, b, vtype=GRB.BINARY, name="matrix")

    # Every object occurs in exactly r blocks.
    for i in range(v):
        model.addConstr(matrix.sum(i, "*") == r, name=f"row[{i}]")

    # Every block contains exactly k objects.
    for j in range(b):
        model.addConstr(matrix.sum("*", j) == k, name=f"col[{j}]")

    # Every two distinct objects occur together in exactly lambda blocks: the
    # scalar product of their rows is lambda. both[i1, i2, j] is the product
    # matrix[i1, j] * matrix[i2, j], stated as a Gurobi AND constraint (one
    # general constraint each) because three linear inequalities per product
    # exceed the licence's 2000-constraint limit at v = b = 13.
    for i1 in range(v):
        for i2 in range(i1 + 1, v):
            both = [model.addVar(vtype=GRB.BINARY, name=f"both[{i1},{i2},{j}]") for j in range(b)]
            for j in range(b):
                model.addConstr(both[j] == gp.and_(matrix[i1, j], matrix[i2, j]), name=f"and[{i1},{i2},{j}]")
            model.addConstr(gp.quicksum(both) == lam, name=f"pair[{i1},{i2}]")

    return model, {"matrix": [[matrix[i, j] for j in range(b)] for i in range(v)]}
