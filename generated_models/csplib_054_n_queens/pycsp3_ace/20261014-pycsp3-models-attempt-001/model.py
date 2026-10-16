from pycsp3 import *

n = data.n

# queens[i] is the column of the queen in row i, counted from 1 to n
queens = VarArray(size=n, dom=range(1, n + 1))

satisfy(
    # no two queens share a column
    AllDifferent(queens),
    # no two queens share a diagonal going up
    AllDifferent([queens[i] + i for i in range(n)]),
    # no two queens share a diagonal going down
    AllDifferent([queens[i] - i for i in range(n)]),
)
