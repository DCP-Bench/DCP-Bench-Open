from pycsp3 import *
from itertools import product

# find the densest still life pattern on an n by m active grid, cells outside the grid are dead
n, m = data.n, data.m

# grid[i][j] is 1 if the cell in row i, column j of the active grid is alive
grid = VarArray(size=[n, m], dom={0, 1})


def around(i, j):
    # the cells around (i, j) that are inside the active grid; cells outside it are dead and do not count
    return [(a, b) for a in range(i - 1, i + 2) for b in range(j - 1, j + 2)
            if (a, b) != (i, j) and 0 <= a < n and 0 <= b < m]


def inside_supports(k):
    # value combinations of a live or dead cell (first value) and its k neighbours that obey the two rules
    return [(c,) + bits for c in (0, 1) for bits in product([0, 1], repeat=k)
            if (c == 1 and sum(bits) in (2, 3)) or (c == 0 and sum(bits) != 3)]


def outside_supports(k):
    # value combinations of the neighbours of a dead cell outside the grid: exactly 3 live is not allowed
    return [bits for bits in product([0, 1], repeat=k) if sum(bits) != 3]


def symmetries(n, m):
    # the flips of the grid, and the turns and diagonal reflections when the grid is square
    maps = [lambda i, j: (n - 1 - i, j), lambda i, j: (i, m - 1 - j), lambda i, j: (n - 1 - i, m - 1 - j)]
    if n == m:
        maps += [lambda i, j: (j, i), lambda i, j: (m - 1 - j, n - 1 - i),
                 lambda i, j: (j, n - 1 - i), lambda i, j: (m - 1 - j, i)]
    return maps


satisfy(
    # a live cell must have 2 or 3 live neighbours, a dead cell must not have exactly 3 live neighbours
    [Table(scope=[grid[i][j]] + [grid[a][b] for (a, b) in around(i, j)], supports=inside_supports(len(around(i, j))))
     for i in range(n) for j in range(m)],
    # a dead cell just outside the active grid must not have exactly 3 live neighbours
    [Table(scope=[grid[a][b] for (a, b) in around(i, j)], supports=outside_supports(len(around(i, j))))
     for i in range(-1, n + 1) for j in range(-1, m + 1)
     if not (0 <= i < n and 0 <= j < m) and len(around(i, j)) >= 3],
    # the pattern is the same when flipped or turned, so only the first of each equivalent pattern is kept:
    # the flat grid, read row by row, is lexicographically no larger than each of its flipped or turned copies
    [LexIncreasing([[grid[i][j] for i in range(n) for j in range(m)],
                    [grid[f(i, j)[0]][f(i, j)[1]] for i in range(n) for j in range(m)]])
     for f in symmetries(n, m)],
)

# maximise the number of live cells in the active grid
maximize(Sum(grid))
