from pycsp3 import *

m = data.m

# the m*m cells of the table, numbered row by row
cells = VarArray(size=m * m, dom=range(m))
# the table: cell (i, j) is the product of i and j, with values 0 to m-1
quasigroup = [[cells[i * m + j] for j in range(m)] for i in range(m)]

satisfy(
    # each row of the table holds every value once
    [AllDifferent(quasigroup[i]) for i in range(m)],
    # each column of the table holds every value once
    [AllDifferent([quasigroup[i][j] for i in range(m)]) for j in range(m)],
)

# (a*b)*(b*a) = a for every pair a, b
# the position in the flattened table of the product (a*b)*(b*a), one position per pair a, b
positions = VarArray(size=m * m, dom=range(m * m))
satisfy(
    # the product a*b is the cell at row a, column b, and the product b*a is the cell at row b, column a
    [positions[a * m + b] == m * cells[a * m + b] + cells[b * m + a] for a in range(m) for b in range(m)],
    # the cell at that position holds a
    [cells[positions[a * m + b]] == a for a in range(m) for b in range(m)],
)
