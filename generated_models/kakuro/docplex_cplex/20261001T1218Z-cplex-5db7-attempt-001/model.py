"""Kakuro: fill the white cells of an n-by-n grid with digits 1..9 so that the digits of every
segment (a run of cells with a clue) add up to the clue and are all different. Blank cells
hold 0.

The model reports the grid.
"""
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]                # size of the grid
    problem = instance["problem"]    # segments as [sum, [row, col], [row, col], ...], 1-based
    blanks = instance["blanks"]      # blank cells as [row, col], 1-based

    digits = range(1, 10)
    blank = {(r - 1, c - 1) for r, c in blanks}
    segments = [(seg[0], [(r - 1, c - 1) for r, c in seg[1:]]) for seg in problem]
    white = {cell for _, cells in segments for cell in cells}

    model = Model("kakuro")

    # has[cell, d] is 1 when a cell of some segment holds digit d. The values of these cells
    # are positive, so 1..9; each holds one digit. A cell that is both blank and in a segment
    # cannot be filled, so it gets no digits at all.
    has = {}
    for cell in white:
        options = [] if cell in blank else digits
        for d in options:
            has[cell, d] = model.binary_var(name=f"has_{cell[0]}_{cell[1]}_{d}")
        model.add_constraint(model.sum(has[cell, d] for d in options) == 1)

    # x[i][j] is the number in cell (i, j): 0 in a blank, the digit in a segment cell, and
    # anything in 0..9 (as in the reference) in a cell that is neither.
    x = []
    for i in range(n):
        row = []
        for j in range(n):
            if (i, j) in white:
                row.append(model.sum(d * has[(i, j), d] for d in digits if ((i, j), d) in has))
            elif (i, j) in blank:
                row.append(0)
            else:
                row.append(model.integer_var(0, 9, name=f"x_{i}_{j}"))
        x.append(row)

    for total, cells in segments:
        # The numbers of the segment add up to its sum.
        model.add_constraint(model.sum(x[r][c] for r, c in cells) == total)
        # All numbers in this segment must be distinct.
        if len(cells) > 1:
            for d in digits:
                model.add_constraint(model.sum(has[cell, d] for cell in cells if (cell, d) in has) <= 1)

    return model, {"x": x}
