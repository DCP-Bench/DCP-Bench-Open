# Quasigroup completion (csplib 067): complete a partially filled order N Latin square.
import mip


def build(instance):
    n = instance["N"]
    start = instance["start"]
    values = range(1, n + 1)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[i][j][v] = 1 if cell (i, j) holds value v (0-based i, j; values 1..N)
    x = [[[model.add_var(f"x_{i}_{j}_{v}", var_type=mip.BINARY) for v in values]
          for j in range(n)] for i in range(n)]

    # the puzzle: the value of each cell, an integer in 1..N
    puzzle = [[model.add_var(f"puzzle_{i}_{j}", lb=1, ub=n, var_type=mip.INTEGER)
               for j in range(n)] for i in range(n)]

    # each cell of the quasigroup holds exactly one value
    for i in range(n):
        for j in range(n):
            model.add_constr(mip.xsum(x[i][j][v - 1] for v in values) == 1)

    # the puzzle value of a cell is the value it holds
    for i in range(n):
        for j in range(n):
            model.add_constr(puzzle[i][j] == mip.xsum(v * x[i][j][v - 1] for v in values))

    # each row contains each element from 1 to N exactly once
    for i in range(n):
        for v in values:
            model.add_constr(mip.xsum(x[i][j][v - 1] for j in range(n)) == 1)

    # each column contains each element from 1 to N exactly once
    for j in range(n):
        for v in values:
            model.add_constr(mip.xsum(x[i][j][v - 1] for i in range(n)) == 1)

    # the given cells keep their pre-filled value; 0 marks an empty cell
    for i in range(n):
        for j in range(n):
            given = start[i][j]
            if given != 0:
                model.add_constr(x[i][j][given - 1] == 1)

    return model, {"puzzle": puzzle}
