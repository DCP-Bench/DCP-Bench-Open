from pycsp3 import *

N = data.N
# the completed quasigroup: an N x N table with values 1 to N
puzzle = VarArray(size=[N, N], dom=range(1, N + 1))

satisfy(
    # each element occurs exactly once in every row
    [AllDifferent(puzzle[i]) for i in range(N)],
    # each element occurs exactly once in every column
    [AllDifferent(puzzle[:, j]) for j in range(N)],
    # the given cells keep their values
    [puzzle[i][j] == data.start[i][j] for i in range(N) for j in range(N) if data.start[i][j] != 0],
)
