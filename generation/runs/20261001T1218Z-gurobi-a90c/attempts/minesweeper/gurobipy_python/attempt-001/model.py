"""Minesweeper: decide which unopened cells hold mines so that every number counts the mines around its cell."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    unopened = instance["X"]
    game = instance["game_data"]
    rows = len(game)
    cols = len(game[0])

    model = gp.Model("minesweeper")

    # mines[r, c] is 1 when cell (r, c) holds a mine.
    mines = model.addVars(rows, cols, vtype=GRB.BINARY, name="mines")

    for r in range(rows):
        for c in range(cols):
            val = game[r][c]
            if val != unopened:
                # An opened cell shows a number, so it cannot be a mine.
                model.addConstr(mines[r, c] == 0, name=f"open[{r},{c}]")
                # The number equals the count of mines among its up to eight neighbours.
                model.addConstr(
                    gp.quicksum(mines[r + a, c + b]
                                for a in (-1, 0, 1) for b in (-1, 0, 1)
                                if (a, b) != (0, 0) and 0 <= r + a < rows and 0 <= c + b < cols)
                    == val,
                    name=f"count[{r},{c}]")

    return model, {"mines": [[mines[r, c] for c in range(cols)] for r in range(rows)]}
