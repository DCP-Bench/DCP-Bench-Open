from pycsp3 import *

# Place coins on an n by n grid, exactly c coins in each row and each column,
# at most one coin per cell, minimising the sum of the squared horizontal
# distances of the coins from the main diagonal.

n = data.n
c = data.c

# x[i][j] is 1 when a coin is placed in row i, column j
x = VarArray(size=[n, n], dom={0, 1})

# z is the sum of the squared horizontal distances from the main diagonal
z = Var(dom=range(0, c * n * (n - 1) * (n - 1) + 1))

satisfy(
    # in each row exactly c coins must be placed
    [Sum(x[i]) == c for i in range(n)],

    # in each column exactly c coins must be placed
    [Sum(x[:, j]) == c for j in range(n)],

    # the sum of the quadratic horizontal distance from the main diagonal of all cells containing a coin
    z == Sum(x[i][j] * (i - j) * (i - j) for i in range(n) for j in range(n) if i != j),
)

# minimise the sum of the quadratic distances from the main diagonal
minimize(z)
