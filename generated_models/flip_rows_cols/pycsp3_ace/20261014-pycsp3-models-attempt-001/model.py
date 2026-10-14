from pycsp3 import *

# Flip the signs of rows and columns of an integer matrix so that every row and every column has a
# positive sum (or zero), and make the overall sum of the resulting matrix as small as possible.
M = data.input_matrix
R = len(M)
C = len(M[0])

# row_signs[i] is -1 if row i is flipped, 1 otherwise; col_signs[j] likewise for column j
row_signs = VarArray(size=R, dom={-1, 1})
col_signs = VarArray(size=C, dom={-1, 1})

# sign[i][j] is the sign of cell (i, j) after the flips, the product of its row and column signs
sign = VarArray(size=[R, C], dom={-1, 1})
# the four sign combinations of a row and a column, and the sign of their product
product_supports = [(a, b, a * b) for a in (-1, 1) for b in (-1, 1)]

satisfy(
    # the sign of a cell is the product of the sign of its row and the sign of its column
    [Table(scope=[row_signs[i], col_signs[j], sign[i][j]], supports=product_supports)
     for i in range(R) for j in range(C)],
    # every row has a sum that is positive or zero
    [Sum(M[i][j] * sign[i][j] for j in range(C)) >= 0 for i in range(R)],
    # every column has a sum that is positive or zero
    [Sum(M[i][j] * sign[i][j] for i in range(R)) >= 0 for j in range(C)],
)

# the overall sum of the matrix after the flips is as small as possible
minimize(
    Sum(M[i][j] * sign[i][j] for i in range(R) for j in range(C))
)
