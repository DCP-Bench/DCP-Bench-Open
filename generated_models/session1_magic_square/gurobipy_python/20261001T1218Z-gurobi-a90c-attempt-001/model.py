"""Magic square: fill an n-by-n grid with the integers 1..n^2, all different, so that every row, column and both diagonals sum to n(n^2+1)/2."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    cells = [(i, j) for i in range(n) for j in range(n)]
    values = range(1, n * n + 1)
    magic_sum = n * (n * n + 1) // 2

    model = gp.Model("magic_square")

    # holds[i, j, v] is 1 when cell (i, j) contains v; the square reads it back.
    holds = model.addVars(range(n), range(n), values, vtype=GRB.BINARY, name="holds")
    square = [[gp.quicksum(v * holds[i, j, v] for v in values) for j in range(n)] for i in range(n)]

    # Every cell holds exactly one number.
    for (i, j) in cells:
        model.addConstr(holds.sum(i, j, "*") == 1, name=f"cell[{i},{j}]")

    # All numbers in the square are different: each of 1..n^2 is used once.
    for v in values:
        model.addConstr(holds.sum("*", "*", v) == 1, name=f"value[{v}]")

    # Every row sums to the magic sum.
    for i in range(n):
        model.addConstr(gp.quicksum(square[i][j] for j in range(n)) == magic_sum, name=f"row[{i}]")

    # Every column sums to the magic sum.
    for j in range(n):
        model.addConstr(gp.quicksum(square[i][j] for i in range(n)) == magic_sum, name=f"col[{j}]")

    # The main diagonal and the other diagonal sum to the magic sum.
    model.addConstr(gp.quicksum(square[i][i] for i in range(n)) == magic_sum, name="diag")
    model.addConstr(gp.quicksum(square[i][n - 1 - i] for i in range(n)) == magic_sum, name="anti_diag")

    return model, {"square": square}
