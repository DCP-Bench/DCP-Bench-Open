from pycsp3 import *

# fill an n by n grid with the numbers 1 to n*n, following the movement rules
n = data.n
N = n * n

# flat[p] is the number written in square p (row-major order)
flat = VarArray(size=N, dom=range(1, N + 1))
# the grid as nested lists, x[i][j] is the number in row i, column j
x = [[flat[i * n + j] for j in range(n)] for i in range(n)]

# pos[k] is the square holding the number k + 1
pos = VarArray(size=N, dom=range(N))

# squares a move can go between: vertically or horizontally exactly three squares away,
# or diagonally exactly two squares away
allowed = [
    (p, q)
    for p in range(N) for q in range(N)
    if (abs(p // n - q // n), abs(p % n - q % n)) in [(0, 3), (3, 0), (2, 2)]
]

satisfy(
    # every square gets a different number
    AllDifferent(flat),
    # the number k + 1 is written in the square pos[k]
    [flat[pos[k]] == k + 1 for k in range(N)],
    # the next number must be placed in a square allowed by the movement rules
    [Table(scope=[pos[k], pos[k + 1]], supports=allowed) for k in range(N - 1)],
)
