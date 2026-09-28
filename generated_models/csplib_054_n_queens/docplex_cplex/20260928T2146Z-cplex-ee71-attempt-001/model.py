"""N-queens: place n queens on an n-by-n board so that no two share a row, a column or a diagonal."""
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]
    rows = range(n)
    cols = range(n)

    model = Model("n_queens")

    # queen[i, j] is 1 when the queen of row i stands in column j.
    queen = model.binary_var_matrix(rows, cols, name="queen")

    # Every row has exactly one queen.
    for i in rows:
        model.add_constraint(model.sum(queen[i, j] for j in cols) == 1, ctname=f"row_{i}")

    # No two queens share a column.
    for j in cols:
        model.add_constraint(model.sum(queen[i, j] for i in rows) <= 1, ctname=f"col_{j}")

    # No two queens share a diagonal: squares with the same j - i lie on one
    # diagonal, and squares with the same j + i on one anti-diagonal.
    for d in range(-(n - 1), n):
        model.add_constraint(model.sum(queen[i, i + d] for i in rows if 0 <= i + d < n) <= 1,
                             ctname=f"diag_{d + n}")
    for s in range(2 * n - 1):
        model.add_constraint(model.sum(queen[i, s - i] for i in rows if 0 <= s - i < n) <= 1,
                             ctname=f"anti_{s}")

    # The column, 1-based, of the queen in each row.
    return model, {"queens": [model.sum((j + 1) * queen[i, j] for j in cols) for i in rows]}
