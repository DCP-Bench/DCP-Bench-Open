from pycsp3 import *

n = data.n
N = n * n  # the number of squares, numbered row by row

# square[k] is the square visited at move k
square = VarArray(size=N, dom=range(N))
# move[p] is the move number at which square p is visited
move = VarArray(size=N, dom=range(N))

satisfy(
    # every square is visited exactly once
    AllDifferent(square),
    # move is the inverse of square: square k is visited at move k
    Channel(square, move),
)

# a knight moves two squares in one direction and one square in the other direction
knight_pairs = []
for p in range(N):
    r, c = divmod(p, n)
    for dr, dc in [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]:
        if 0 <= r + dr < n and 0 <= c + dc < n:
            knight_pairs.append((p, (r + dr) * n + (c + dc)))

satisfy(
    # each move goes from one square to a square a knight's move away
    [Table(scope=[square[k], square[k + 1]], supports=knight_pairs) for k in range(N - 1)],
)

# the chessboard: the entry of each square is its move number, numbered row by row
x = [[move[i * n + j] for j in range(n)] for i in range(n)]
