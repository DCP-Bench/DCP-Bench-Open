"""Flow Free: colour every cell so that each pair of equal endpoints is joined by a non-crossing pipe."""
import gurobipy as gp
from gurobipy import GRB

# The reference gives every cell a colour in 1..10 (wider than the five pairs
# on the board); the range is widened if the board uses a larger colour.
REFERENCE_MAX_COLOUR = 10


def build(instance):
    board = instance["board"]
    rows, cols = len(board), len(board[0])
    top = max([REFERENCE_MAX_COLOUR] + [v for row in board for v in row])
    colours = range(1, top + 1)
    cells = [(i, j) for i in range(rows) for j in range(cols)]

    model = gp.Model("flow_free_game")

    # paint[i, j, c] = 1 when cell (i, j) has colour c; B[i][j] reads it back.
    paint = model.addVars(rows, cols, colours, vtype=GRB.BINARY, name="paint")
    for i, j in cells:
        model.addConstr(paint.sum(i, j, "*") == 1, name=f"one_colour[{i},{j}]")
    B = [[gp.quicksum(c * paint[i, j, c] for c in colours) for j in range(cols)] for i in range(rows)]

    # same[e] = 1 when the two orthogonally adjacent cells of edge e share a colour:
    # it is forced on when both have colour c, and off when one has colour c
    # and the other does not.
    edges = [((i, j), (i + di, j + dj)) for i, j in cells for di, dj in ((0, 1), (1, 0))
             if i + di < rows and j + dj < cols]
    same = {}
    for (u, v) in edges:
        s = model.addVar(vtype=GRB.BINARY, name=f"same[{u},{v}]")
        for c in colours:
            model.addConstr(s >= paint[u + (c,)] + paint[v + (c,)] - 1)
            model.addConstr(s <= 1 - paint[u + (c,)] + paint[v + (c,)])
        same[u, v] = same[v, u] = s

    def same_neighbours(i, j):
        return gp.quicksum(same[(i, j), (k, l)] for k, l in
                           ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                           if 0 <= k < rows and 0 <= l < cols)

    for i, j in cells:
        if board[i][j] != 0:
            # An endpoint keeps its colour and continues into exactly one
            # neighbour of the same colour.
            model.addConstr(paint[i, j, board[i][j]] == 1, name=f"endpoint[{i},{j}]")
            model.addConstr(same_neighbours(i, j) == 1, name=f"pipe_end[{i},{j}]")
        else:
            # An empty cell lies on a pipe: exactly two neighbours share its colour.
            model.addConstr(same_neighbours(i, j) == 2, name=f"pipe_middle[{i},{j}]")

    return model, {"B": B}
