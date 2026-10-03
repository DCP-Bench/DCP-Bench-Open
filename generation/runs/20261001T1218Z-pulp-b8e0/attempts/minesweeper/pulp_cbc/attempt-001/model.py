"""Minesweeper: the board shows, for every opened cell, the number of mines in the (up to
eight) cells around it; the other cells are not opened. Decide which cells hold a mine.

The model reports for every cell whether it is a mine.
"""
import pulp


def build(instance):
    unopened = instance["X"]  # the value that marks a cell that is not opened
    game = instance["game_data"]  # game[r][c] = number of mines around the cell, or `unopened`
    rows, cols = len(game), len(game[0])

    problem = pulp.LpProblem("minesweeper", pulp.LpMinimize)  # satisfaction: no objective

    # mines[r][c] = 1 if the cell holds a mine
    mines = [[pulp.LpVariable(f"mines_{r}_{c}", cat="Binary") for c in range(cols)]
             for r in range(rows)]

    for r in range(rows):
        for c in range(cols):
            if game[r][c] != unopened:
                # an opened cell is not a mine
                problem += mines[r][c] == 0
                # the number shown is the number of mines in the cells around it
                problem += pulp.lpSum(
                    mines[r + a][c + b]
                    for a in (-1, 0, 1) for b in (-1, 0, 1)
                    if (a, b) != (0, 0) and 0 <= r + a < rows and 0 <= c + b < cols
                ) == game[r][c]

    return problem, {"mines": mines}
