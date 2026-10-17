# Sudoku: fill a 9x9 grid with numbers so that each row, column and 3x3 section
# contains all the digits between 1 and 9. The input grid has some cells filled
# with numbers and some empty (0). Output: the solved grid "grid" as a 9x9 list.
import mip


def build(instance):
    givens = instance["input_grid"]
    n = len(givens)  # 9
    box = 3
    digits = range(1, n + 1)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Binary x[i][j][v] = 1 when cell (i, j) holds digit v.
    x = [[[model.add_var(f"x_{i}_{j}_{v}", var_type=mip.BINARY)
           for v in digits] for j in range(n)] for i in range(n)]

    # The grid output: the digit of each cell, an integer in 1..9.
    grid = [[model.add_var(f"g_{i}_{j}", lb=1, ub=n, var_type=mip.INTEGER)
             for j in range(n)] for i in range(n)]

    # Each cell holds exactly one digit, and the grid value is that digit.
    for i in range(n):
        for j in range(n):
            model.add_constr(mip.xsum(x[i][j][k] for k in range(n)) == 1)
            model.add_constr(
                grid[i][j] == mip.xsum(v * x[i][j][v - 1] for v in digits))

    # Clues: the cells filled with numbers keep their value.
    # Empty cells (0) are left free.
    for i in range(n):
        for j in range(n):
            clue = givens[i][j]
            if clue != 0:
                model.add_constr(x[i][j][clue - 1] == 1)

    # Each row contains all the digits between 1 and 9.
    for i in range(n):
        for v in digits:
            model.add_constr(mip.xsum(x[i][j][v - 1] for j in range(n)) == 1)

    # Each column contains all the digits between 1 and 9.
    for j in range(n):
        for v in digits:
            model.add_constr(mip.xsum(x[i][j][v - 1] for i in range(n)) == 1)

    # Each 3x3 section contains all the digits between 1 and 9.
    for bi in range(0, n, box):
        for bj in range(0, n, box):
            for v in digits:
                model.add_constr(mip.xsum(
                    x[i][j][v - 1]
                    for i in range(bi, bi + box)
                    for j in range(bj, bj + box)) == 1)

    # Satisfaction problem: no objective.
    return model, {"grid": grid}
