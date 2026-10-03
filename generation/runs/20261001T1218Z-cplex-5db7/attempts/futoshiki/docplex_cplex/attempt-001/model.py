"""Futoshiki: fill an n-by-n grid with 1..n so that every row and every column holds different
numbers, the given numbers stay, and every "less than" sign between two cells holds.

The model reports the filled grid.
"""
from docplex.mp.model import Model


def build(instance):
    values = instance["values"]  # values[i][j]: the given number in row i, column j; 0 if not set
    lt = instance["lt"]          # [i1, j1, i2, j2], 1-based: cell (i1, j1) < cell (i2, j2)
    size = len(values)
    cells = range(size)
    numbers = range(1, size + 1)

    model = Model("futoshiki")

    # has[i, j, v] is 1 when cell (i, j) holds v; every cell holds one number.
    has = {(i, j, v): model.binary_var(name=f"has_{i}_{j}_{v}") for i in cells for j in cells for v in numbers}
    for i in cells:
        for j in cells:
            model.add_constraint(model.sum(has[i, j, v] for v in numbers) == 1)
    grid = [[model.sum(v * has[i, j, v] for v in numbers) for j in cells] for i in cells]

    # Set the initial values.
    for i in cells:
        for j in cells:
            if values[i][j] > 0:
                model.add_constraint(grid[i][j] == values[i][j])

    # All rows have to be different, and all columns: each number once per row and column.
    for v in numbers:
        for i in cells:
            model.add_constraint(model.sum(has[i, j, v] for j in cells) == 1)
        for j in cells:
            model.add_constraint(model.sum(has[i, j, v] for i in cells) == 1)

    # All "less than" constraints are satisfied (the positions are 1-based).
    for i1, j1, i2, j2 in lt:
        model.add_constraint(grid[i1 - 1][j1 - 1] + 1 <= grid[i2 - 1][j2 - 1])

    return model, {"grid": grid}
