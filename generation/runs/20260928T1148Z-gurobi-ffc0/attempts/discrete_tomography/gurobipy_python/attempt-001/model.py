"""Discrete tomography: rebuild a 0/1 matrix from the number of ones in each row and each column."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    row_sums = instance["row_sums"]
    col_sums = instance["col_sums"]
    rows = range(len(row_sums))
    cols = range(len(col_sums))

    model = gp.Model("discrete_tomography")

    # matrix[i, j] is the 0/1 entry in row i, column j.
    matrix = model.addVars(rows, cols, vtype=GRB.BINARY, name="matrix")

    # Each row holds as many ones as its x-ray says.
    for i in rows:
        model.addConstr(matrix.sum(i, "*") == row_sums[i], name=f"row[{i}]")

    # Each column holds as many ones as its x-ray says.
    for j in cols:
        model.addConstr(matrix.sum("*", j) == col_sums[j], name=f"col[{j}]")

    return model, {"matrix": [[matrix[i, j] for j in cols] for i in rows]}
