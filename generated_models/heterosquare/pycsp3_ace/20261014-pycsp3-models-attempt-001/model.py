from pycsp3 import *

# Heterosquare of order n: the n*n cells hold the distinct integers 1 to n^2, and the sums
# of the rows, the columns and the two diagonals are all different from each other.

n = data.n

# x[i][j] is the number in row i and column j
x = VarArray(size=[n, n], dom=range(1, n * n + 1))

satisfy(
    # the elements of the square are distinct integers from 1 to n^2
    AllDifferent(x),

    # the sums of the rows, columns and diagonals are all different
    AllDifferent(
        [Sum(x[i]) for i in range(n)]
        + [Sum(x[i][j] for i in range(n)) for j in range(n)]
        + [Sum(x[i][i] for i in range(n)), Sum(x[i][n - 1 - i] for i in range(n))]
    ),
)
