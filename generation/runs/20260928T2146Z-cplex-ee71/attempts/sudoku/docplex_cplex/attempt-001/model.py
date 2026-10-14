"""Sudoku: fill the 9-by-9 grid so that every row, column and 3-by-3 box holds each digit 1..9 once."""
from docplex.mp.model import Model

# The grid, its boxes and its digits are fixed by the rules of Sudoku.
SIZE, BOX = 9, 3
CELLS = range(SIZE)
DIGITS = range(1, SIZE + 1)


def build(instance):
    given = instance["input_grid"]  # 0 marks an empty cell

    model = Model("sudoku")

    # holds[r, c, d] is 1 when the cell in row r, column c holds digit d.
    holds = model.binary_var_cube(CELLS, CELLS, DIGITS, name="holds")

    # Every cell holds exactly one digit, and a given cell keeps its digit.
    for r in CELLS:
        for c in CELLS:
            model.add_constraint(model.sum(holds[r, c, d] for d in DIGITS) == 1, ctname=f"cell_{r}_{c}")
            if given[r][c] != 0:
                holds[r, c, given[r][c]].lb = 1

    # Each digit appears once in every row and once in every column.
    for d in DIGITS:
        for r in CELLS:
            model.add_constraint(model.sum(holds[r, c, d] for c in CELLS) == 1, ctname=f"row_{r}_{d}")
        for c in CELLS:
            model.add_constraint(model.sum(holds[r, c, d] for r in CELLS) == 1, ctname=f"col_{c}_{d}")

    # Each digit appears once in every 3-by-3 box.
    for d in DIGITS:
        for top in range(0, SIZE, BOX):
            for left in range(0, SIZE, BOX):
                model.add_constraint(model.sum(holds[r, c, d] for r in range(top, top + BOX)
                                               for c in range(left, left + BOX)) == 1,
                                     ctname=f"box_{top}_{left}_{d}")

    grid = [[model.sum(d * holds[r, c, d] for d in DIGITS) for c in CELLS] for r in CELLS]
    return model, {"grid": grid}
