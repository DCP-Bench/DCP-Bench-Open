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

# rowcost[i] is the sum of the squared distances of the coins in row i
rowcost = VarArray(size=n, dom=range(0, max_row + 1))

# colcost[j] is the sum of the squared distances of the coins in column j
colcost = VarArray(size=n, dom=range(0, max_row + 1))

# z is the sum of the squared horizontal distances from the main diagonal
z = Var(dom=range(min_total, n * max_row + 1))

satisfy(
    # in each row exactly c coins must be placed
    [Sum(x[i]) == c for i in range(n)],

    # in each column exactly c coins must be placed
    [Sum(x[:, j]) == c for j in range(n)],

    # the cost of each row is the sum of the squared distances from the diagonal of its coins
    [rowcost[i] == Sum(x[i][j] * (i - j) * (i - j) for j in range(n)) for i in range(n)],

    # the cost of each column is the sum of the squared distances from the diagonal of its coins
    [colcost[j] == Sum(x[i][j] * (i - j) * (i - j) for i in range(n)) for j in range(n)],

    # the sum of the quadratic horizontal distance from the main diagonal of all cells containing a coin
    z == Sum(rowcost),
    z == Sum(colcost),
)

# minimise the sum of the quadratic distances from the main diagonal
minimize(z)
