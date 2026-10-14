# Problem: Colour the board so that each colour forms one pipe between its two endpoints, covering every cell without overlap.
from pycsp3 import *

board = data.board
n = len(board)
colours = max(max(row) for row in board)
DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]
cells = [(i, j) for i in range(n) for j in range(n)]


def inside(i, j):
    return 0 <= i < n and 0 <= j < n


# horizontally and vertically adjacent pairs of cells
edges = [((i, j), (i + di, j + dj)) for i, j in cells for di, dj in DIRECTIONS[:2] if inside(i + di, j + dj)]
endpoints = [(i, j) for i, j in cells if board[i][j] > 0]
# the root of each pipe is its first endpoint in reading order
roots = [min(p for p in endpoints if board[p[0]][p[1]] == c) for c in range(1, colours + 1)]
# B[i][j] is the B of the cell in row i and column j
B = VarArray(size=[n, n], dom=range(1, colours + 1))
# same[e] = 1 if the two cells of edge e have the same B
same = VarArray(size=len(edges), dom={0, 1})
# parent[cell * 4 + k] = 1 if the neighbour in direction k is the cell before this one on its pipe
parent = VarArray(size=n * n * 4, dom={0, 1})
# depth[i][j] is the number of steps from the root of the pipe to the cell
depth = VarArray(size=[n, n], dom=range(0, n * n))
satisfy(
    # the pre-coloured cells keep their colours
    [B[i][j] == board[i][j] for i, j in endpoints],
    # two neighbouring cells are joined by a pipe piece when they have the same B
    [(same[e] == 1) == (B[p[0]][p[1]] == B[q[0]][q[1]]) for e, (p, q) in enumerate(edges)],
    # a pipe end has one neighbour of its B, every other cell has two
    [Sum(same[e] for e, (p, q) in enumerate(edges) if cell in (p, q)) == (1 if cell in endpoints else 2) for cell in cells],
    # the directions that lead off the board are never a parent
    [parent[(i * n + j) * 4 + k] == 0 for i, j in cells for k, (di, dj) in enumerate(DIRECTIONS) if not inside(i + di, j + dj)],
    # every cell except the root of its pipe has exactly one parent
    [Sum(parent[(i * n + j) * 4:(i * n + j) * 4 + 4]) == (0 if (i, j) in roots else 1) for i, j in cells],
    # a parent has the same B
    [imply(parent[(i * n + j) * 4 + k] == 1, B[i][j] == B[i + di][j + dj]) for i, j in cells for k, (di, dj) in enumerate(DIRECTIONS) if inside(i + di, j + dj)],
    # the parent is one step closer to the root, so every cell of a pipe is connected to its root
    [imply(parent[(i * n + j) * 4 + k] == 1, depth[i][j] == depth[i + di][j + dj] + 1) for i, j in cells for k, (di, dj) in enumerate(DIRECTIONS) if inside(i + di, j + dj)],
    # the roots are at distance zero
    [depth[i][j] == 0 for i, j in roots],
)
