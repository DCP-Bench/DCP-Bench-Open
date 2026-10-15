# Flip the signs of whole rows and columns of a matrix so that every row and every
# column sums to a non-negative number, and minimise the total sum of the result.
from pyscipopt import Model, quicksum


def build(instance):
    a = instance["input_matrix"]
    n_rows = len(a)
    n_cols = len(a[0])
    m = Model()

    # row_flip[i] = 1 if row i has its sign flipped (sign -1)
    row_flip = [m.addVar(name=f"row_flip[{i}]", vtype="B") for i in range(n_rows)]
    # col_flip[j] = 1 if column j has its sign flipped (sign -1)
    col_flip = [m.addVar(name=f"col_flip[{j}]", vtype="B") for j in range(n_cols)]

    # cell_flip[i, j] = 1 if cell (i, j) changes sign: exactly one of its row and
    # column is flipped, so the parity of row_flip[i] + col_flip[j] + cell_flip[i, j] is even
    cell_flip = {}
    for i in range(n_rows):
        for j in range(n_cols):
            f = m.addVar(name=f"cell_flip[{i},{j}]", vtype="B")
            m.addConsXor([row_flip[i], col_flip[j], f], False)
            cell_flip[i, j] = f

    # the signed value of cell (i, j) is a[i][j] * (1 - 2 * cell_flip[i, j])
    # every row sums to a non-negative number after the flips
    for i in range(n_rows):
        m.addCons(quicksum(a[i][j] - 2 * a[i][j] * cell_flip[i, j] for j in range(n_cols)) >= 0)
    # every column sums to a non-negative number after the flips
    for j in range(n_cols):
        m.addCons(quicksum(a[i][j] - 2 * a[i][j] * cell_flip[i, j] for i in range(n_rows)) >= 0)

    # minimise the overall sum of the signed matrix
    m.setObjective(
        quicksum(a[i][j] - 2 * a[i][j] * cell_flip[i, j] for i in range(n_rows) for j in range(n_cols)),
        "minimize",
    )

    # the outputs are the signs (1 or -1) of rows and columns
    row_signs = [1 - 2 * row_flip[i] for i in range(n_rows)]
    col_signs = [1 - 2 * col_flip[j] for j in range(n_cols)]
    return m, {"row_signs": row_signs, "col_signs": col_signs}
