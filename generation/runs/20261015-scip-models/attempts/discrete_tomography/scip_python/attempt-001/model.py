# Discrete tomography: find a 0/1 matrix whose row sums and column sums match the
# given counts of ones (the "x-ray" totals in each row and each column).
from pyscipopt import Model, quicksum


def build(instance):
    row_sums = instance["row_sums"]
    col_sums = instance["col_sums"]
    nrows = len(row_sums)
    ncols = len(col_sums)

    m = Model()
    # x[i, j] = 1 if cell (row i, column j) contains a one
    x = {(i, j): m.addVar(name=f"x_{i}_{j}", vtype="B") for i in range(nrows) for j in range(ncols)}

    # each row contains as many ones as its row total says
    for i in range(nrows):
        m.addCons(quicksum(x[i, j] for j in range(ncols)) == row_sums[i])
    # each column contains as many ones as its column total says
    for j in range(ncols):
        m.addCons(quicksum(x[i, j] for i in range(nrows)) == col_sums[j])

    # the output is the 0/1 matrix, one list per row
    matrix = [[x[i, j] for j in range(ncols)] for i in range(nrows)]
    return m, {"matrix": matrix}
