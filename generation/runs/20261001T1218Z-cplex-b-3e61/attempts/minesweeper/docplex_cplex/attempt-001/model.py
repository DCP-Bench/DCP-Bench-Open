"""Minesweeper: decide which unopened cells of the board hold a mine, given that every opened cell
shows the number of mines among its (up to eight) neighbours.

The model reports, for every cell, whether it is a mine.
"""
from docplex.mp.model import Model


def build(instance):
    X = instance["X"]              # marker of an unopened cell
    game = instance["game_data"]   # 0-8: number of mines around the cell, X: not opened
    rows, cols = len(game), len(game[0])

    model = Model("minesweeper")

    # mines[r][c] = 1 if cell (r, c) holds a mine
    mines = [[model.binary_var(name=f"mine_{r}_{c}") for c in range(cols)] for r in range(rows)]

    for r in range(rows):
        for c in range(cols):
            val = game[r][c]
            if val == X:
                continue
            # An opened cell cannot be a mine.
            model.add_constraint(mines[r][c] == 0)
            # The number on an opened cell is the number of mines among its neighbours.
            neighbours = [mines[r + a][c + b]
                          for a in (-1, 0, 1) for b in (-1, 0, 1)
                          if (a, b) != (0, 0) and 0 <= r + a < rows and 0 <= c + b < cols]
            model.add_constraint(model.sum(neighbours) == val)

    return model, {"mines": mines}
