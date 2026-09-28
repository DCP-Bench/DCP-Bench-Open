"""Sudoku: fill the 9-by-9 grid so that every row, column and 3-by-3 box holds each digit 1..9 once."""
import gurobipy as gp
from gurobipy import GRB

# The grid, its boxes and its digits are fixed by the rules of Sudoku.
SIZE, BOX = 9, 3
CELLS = range(SIZE)
DIGITS = range(1, SIZE + 1)


def build(instance):
    given = instance["input_grid"]  # 0 marks an empty cell

    model = gp.Model("sudoku")

    # holds[r, c, d] is 1 when the cell in row r, column c holds digit d.
    holds = model.addVars(CELLS, CELLS, DIGITS, vtype=GRB.BINARY, name="holds")

    # Every cell holds exactly one digit, and a given cell keeps its digit.
    for r in CELLS:
        for c in CELLS:
            model.addConstr(holds.sum(r, c, "*") == 1, name=f"cell[{r},{c}]")
            if given[r][c] != 0:
                holds[r, c, given[r][c]].LB = 1

    # Each digit appears once in every row and once in every column.
    for d in DIGITS:
        for r in CELLS:
            model.addConstr(holds.sum(r, "*", d) == 1, name=f"row[{r},{d}]")
        for c in CELLS:
            model.addConstr(holds.sum("*", c, d) == 1, name=f"col[{c},{d}]")

    # Each digit appears once in every 3-by-3 box.
    for d in DIGITS:
        for top in range(0, SIZE, BOX):
            for left in range(0, SIZE, BOX):
                model.addConstr(gp.quicksum(holds[r, c, d] for r in range(top, top + BOX)
                                            for c in range(left, left + BOX)) == 1,
                                name=f"box[{top},{left},{d}]")

    grid = [[gp.quicksum(d * holds[r, c, d] for d in DIGITS) for c in CELLS] for r in CELLS]
    return model, {"grid": grid}
