from pycsp3 import *

# Magic square of size n: each cell holds a different integer from 1 to n*n, and every row, column and
# diagonal sums to n(n^2 + 1)/2.
n = data.n
magic_sum = n * (n * n + 1) // 2

# square[i][j] is the number in row i and column j
square = VarArray(size=[n, n], dom=range(1, n * n + 1))

satisfy(
    # each cell contains a different number
    AllDifferent([square[i][j] for i in range(n) for j in range(n)]),
    # each row sums to the magic sum
    [Sum(square[i]) == magic_sum for i in range(n)],
    # each column sums to the magic sum
    [Sum(square[i][j] for i in range(n)) == magic_sum for j in range(n)],
    # the main diagonal sums to the magic sum
    Sum(square[i][i] for i in range(n)) == magic_sum,
    # the other diagonal sums to the magic sum
    Sum(square[i][n - 1 - i] for i in range(n)) == magic_sum,
)
