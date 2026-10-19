# Magic square: fill an n x n grid with the distinct integers 1 to n^2 so that every row, column and both diagonals sum to n(n^2+1)/2.
import mip


def build(instance):
    n = instance["n"]
    # the number of cells and the largest value to place
    N = n * n
    # the magic sum n(n^2+1)/2 (always an integer)
    target = n * (N + 1) // 2
    cells = [(i, j) for i in range(n) for j in range(n)]
    values = range(1, N + 1)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # square[i][j] = the integer in row i, column j, between 1 and n^2
    square = [[model.add_var(f"sq_{i}_{j}", lb=1, ub=N, var_type=mip.INTEGER)
               for j in range(n)] for i in range(n)]
    # p[i, j, v] = 1 if cell (i, j) holds the number v (one-hot encoding of the cell value)
    p = {(i, j, v): model.add_var(f"p_{i}_{j}_{v}", var_type=mip.BINARY)
         for (i, j) in cells for v in values}

    # each cell holds exactly one number, and that number is square[i][j]
    for (i, j) in cells:
        model.add_constr(mip.xsum(p[i, j, v] for v in values) == 1, f"one_value_{i}_{j}")
        model.add_constr(square[i][j] == mip.xsum(v * p[i, j, v] for v in values), f"cell_value_{i}_{j}")

    # each cell contains a different integer from 1 to n^2: every number is used exactly once
    for v in values:
        model.add_constr(mip.xsum(p[i, j, v] for (i, j) in cells) == 1, f"each_number_once_{v}")

    # the sum of the integers in each row is equal to n(n^2+1)/2
    for i in range(n):
        model.add_constr(mip.xsum(square[i][j] for j in range(n)) == target, f"row_{i}")

    # the sum of the integers in each column is equal to n(n^2+1)/2
    for j in range(n):
        model.add_constr(mip.xsum(square[i][j] for i in range(n)) == target, f"column_{j}")

    # the sum of the integers on the main diagonal is equal to n(n^2+1)/2
    model.add_constr(mip.xsum(square[i][i] for i in range(n)) == target, "diagonal")

    # the sum of the integers on the other diagonal is equal to n(n^2+1)/2
    model.add_constr(mip.xsum(square[i][n - 1 - i] for i in range(n)) == target, "anti_diagonal")

    return model, {"square": square}
