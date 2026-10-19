# N-queens: place n queens on an n x n chessboard so that no two queens attack each other
# (no two share a row, a column or a diagonal). Output queens[i] is the column (1..n) of the
# queen in row i.
# Encoding: one-hot binaries p[i][v] (row i holds its queen in column v), so every row
# constraint and every column constraint is a sum of binaries; diagonals are sums over
# the cells on one diagonal.
import mip


def build(instance):
    # n is the board size from the instance; the description leaves it open
    n = instance["n"]

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    model.verbose = 0
    model.max_mip_gap = 0.0
    model.max_mip_gap_abs = 0.0

    # p[i][v] = 1 if the queen of row i stands in column v (rows 0-based, columns 1..n)
    cols = range(1, n + 1)
    p = [[model.add_var(f"p_{i}_{v}", var_type=mip.BINARY) for v in cols] for i in range(n)]

    # the queens are placed one per row: every row holds exactly one queen
    for i in range(n):
        model += mip.xsum(p[i][v - 1] for v in cols) == 1

    # no two queens share a column: every column holds at most one queen
    for v in cols:
        model += mip.xsum(p[i][v - 1] for i in range(n)) <= 1

    # no two queens share a diagonal running down-right (constant i - v)
    for d in range(-n, n + 1):
        terms = [p[i][v - 1] for i in range(n) for v in cols if i - v == d]
        if len(terms) > 1:
            model += mip.xsum(terms) <= 1

    # no two queens share a diagonal running down-left (constant i + v)
    for s in range(0, 2 * n + 1):
        terms = [p[i][v - 1] for i in range(n) for v in cols if i + v == s]
        if len(terms) > 1:
            model += mip.xsum(terms) <= 1

    # the output: the column of the queen in each row, as an integer
    queens = []
    for i in range(n):
        q = model.add_var(f"queen_{i}", lb=1, ub=n, var_type=mip.INTEGER)
        model += q == mip.xsum(v * p[i][v - 1] for v in cols)
        queens.append(q)

    return model, {"queens": queens}
