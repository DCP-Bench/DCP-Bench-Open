"""Flip rows and columns (Einav's puzzle): choose a sign for every row and column so that all row and column sums are non-negative and the overall sum is minimal."""
import gurobipy as gp
from gurobipy import GRB

# Bounds the problem's reference model gives its variables, mirrored as
# problem constants: each flipped entry lies in -100..100, each row and column
# sum in 0..300, and the overall sum in 0..1000.
ENTRY_BOUND = 100
LINE_SUM_MAX = 300
TOTAL_MAX = 1000


def build(instance):
    a = instance["input_matrix"]
    rows = len(a)
    cols = len(a[0])

    model = gp.Model("flip_rows_cols")

    # A sign is -1 or +1. row_up[i] is 1 when row i keeps its sign (+1), and
    # col_up[j] likewise, so the sign is 2 * up - 1.
    row_up = [model.addVar(vtype=GRB.BINARY, name=f"row_up[{i}]") for i in range(rows)]
    col_up = [model.addVar(vtype=GRB.BINARY, name=f"col_up[{j}]") for j in range(cols)]

    # Entry (i, j) after flipping is a[i][j] * row_sign * col_sign. The product
    # of the two signs is -1 exactly when they differ, so flipped[i, j] is the
    # XOR of the two up bits, with its four linear inequalities; this avoids a
    # product of variables, which would cut the licence to 200 variables.
    flipped = model.addVars(rows, cols, vtype=GRB.BINARY, name="flipped")
    x = {}
    for i in range(rows):
        for j in range(cols):
            f = flipped[i, j]
            model.addConstr(f >= row_up[i] - col_up[j])
            model.addConstr(f >= col_up[j] - row_up[i])
            model.addConstr(f <= row_up[i] + col_up[j])
            model.addConstr(f <= 2 - row_up[i] - col_up[j])
            x[i, j] = a[i][j] * (1 - 2 * f)

    # Each flipped entry lies within the reference's entry bound. A fixed entry
    # is +-a[i][j], so this only excludes data beyond the bound.
    for i in range(rows):
        for j in range(cols):
            if abs(a[i][j]) > ENTRY_BOUND:
                model.addConstr(flipped[i, j] >= 2, name=f"entry_out_of_range[{i},{j}]")

    # Every row sum and every column sum is non-negative (and at most the
    # reference's bound).
    for i in range(rows):
        row_sum = gp.quicksum(x[i, j] for j in range(cols))
        model.addConstr(row_sum >= 0, name=f"row_nonneg[{i}]")
        model.addConstr(row_sum <= LINE_SUM_MAX, name=f"row_max[{i}]")
    for j in range(cols):
        col_sum = gp.quicksum(x[i, j] for i in range(rows))
        model.addConstr(col_sum >= 0, name=f"col_nonneg[{j}]")
        model.addConstr(col_sum <= LINE_SUM_MAX, name=f"col_max[{j}]")

    # Minimise the overall sum, which lies in 0..1000.
    total_sum = gp.quicksum(x.values())
    model.addConstr(total_sum >= 0, name="total_nonneg")
    model.addConstr(total_sum <= TOTAL_MAX, name="total_max")
    model.setObjective(total_sum, GRB.MINIMIZE)

    row_signs = [2 * u - 1 for u in row_up]
    col_signs = [2 * u - 1 for u in col_up]
    return model, {"row_signs": row_signs, "col_signs": col_signs}
