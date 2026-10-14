from pycsp3 import *

# Place coins on an n by n grid, exactly c coins in each row and each column,
# at most one coin per cell, minimising the sum of the squared horizontal
# distances of the coins from the main diagonal.

n = data.n
c = data.c

# lower bound on the total: each row pays at least for its c cells nearest the diagonal
row_costs = [sorted((i - j) * (i - j) for j in range(n)) for i in range(n)]
min_total = sum(sum(row_costs[i][:c]) for i in range(n))
max_row = c * (n - 1) * (n - 1)

# x[i][j] is 1 when a coin is placed in row i, column j
x = VarArray(size=[n, n], dom={0, 1})

# z is the sum of the squared horizontal distances from the main diagonal
z = Var(dom=range(min_total, n * max_row + 1))

satisfy(
    # in each row exactly c coins must be placed
    [Sum(x[i]) == c for i in range(n)],

    # in each column exactly c coins must be placed
    [Sum(x[:, j]) == c for j in range(n)],

    # the sum of the quadratic horizontal distance from the main diagonal of all cells containing a coin
    z == Sum(x[i][j] * (i - j) * (i - j) for i in range(n) for j in range(n)),

    # transposing the grid keeps the constraints and the cost, so the grid
    # is kept only when its row-major reading is not after its transpose
    LexIncreasing([[x[i][j] for i in range(n) for j in range(n)],
                   [x[j][i] for i in range(n) for j in range(n)]]),
)

# minimise the sum of the quadratic distances from the main diagonal
minimize(z)
