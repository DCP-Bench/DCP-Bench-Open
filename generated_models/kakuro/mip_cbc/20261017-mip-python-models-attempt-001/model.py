# Kakuro: insert a digit from 1 to 9 into each white cell so that the sum of the
# numbers in each entry matches its clue and no digit is duplicated in any entry.
# Output x is an n x n matrix; 0 marks a cell that is not white (blank).
import mip


def build(instance):
    n = instance["n"]
    model = mip.Model(solver_name="CBC")

    # the data's blanks are the cells that are not filled (clue and black cells, 1-based);
    # every other cell of the n x n grid is white
    blank = {(r - 1, c - 1) for r, c in instance["blanks"]}
    white = [(r, c) for r in range(n) for c in range(n) if (r, c) not in blank]
    digits = list(range(1, 10))

    # one value per white cell, from the digits 1 to 9
    value = {}
    pick = {}
    for (r, c) in white:
        value[(r, c)] = model.add_var(f"x_{r}_{c}", lb=1, ub=9, var_type=mip.INTEGER)
        pick[(r, c)] = {}
        for d in digits:
            pick[(r, c)][d] = model.add_var(f"p_{r}_{c}_{d}", var_type=mip.BINARY)
        # each white cell takes exactly one digit
        model.add_constr(mip.xsum(pick[(r, c)][d] for d in digits) == 1)
        # the cell value is the digit that was picked
        model.add_constr(value[(r, c)] == mip.xsum(d * pick[(r, c)][d] for d in digits))

    # the clues: each entry is a list of cells whose digits sum to the clue value
    entries = []
    for segment in instance["problem"]:
        clue = segment[0]
        cells = [(r - 1, c - 1) for r, c in segment[1:]]
        entries.append((clue, cells))

    # the sum of the numbers in each entry matches the clue associated with it
    for clue, cells in entries:
        model.add_constr(mip.xsum(value[cell] for cell in cells) == clue)

    # no digit is duplicated in any entry
    for clue, cells in entries:
        for d in digits:
            model.add_constr(mip.xsum(pick[cell][d] for cell in cells) <= 1)

    x = []
    for r in range(n):
        row = []
        for c in range(n):
            if (r, c) in value:
                row.append(value[(r, c)])
            else:
                row.append(0)
        x.append(row)

    return model, {"x": x}
