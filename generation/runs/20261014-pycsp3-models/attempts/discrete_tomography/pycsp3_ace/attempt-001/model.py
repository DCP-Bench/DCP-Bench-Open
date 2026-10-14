# Discrete tomography: fill a 0/1 matrix so that each row and each column contains the given number of ones.
from pycsp3 import *

row_sums = data.row_sums
col_sums = data.col_sums
rows = len(row_sums)
cols = len(col_sums)

# matrix[i][j] = 1 if the cell in row i and column j holds a one
matrix = VarArray(size=[rows, cols], dom={0, 1})

satisfy(
    # the number of ones in each row is the row sum
    [Sum(matrix[i][j] for j in range(cols)) == row_sums[i] for i in range(rows)],
    # the number of ones in each column is the column sum
    [Sum(matrix[i][j] for i in range(rows)) == col_sums[j] for j in range(cols)],
)
