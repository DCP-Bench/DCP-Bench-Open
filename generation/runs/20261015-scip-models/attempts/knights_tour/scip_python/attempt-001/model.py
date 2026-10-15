# Knight's tour: a knight visits every square of an n x n board exactly once, without returning to its start; the output gives each square's move number.
from pyscipopt import Model, quicksum

KNIGHT_MOVES = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]


def build(instance):
    n = instance["n"]
    N = n * n

    squares = [(r, c) for r in range(n) for c in range(n)]

    # adjacency: the knight's legal moves from each square to the other squares on the board
    succ = {s: [] for s in squares}
    pred = {s: [] for s in squares}
    for (r, c) in squares:
        for dr, dc in KNIGHT_MOVES:
            t = (r + dr, c + dc)
            if 0 <= t[0] < n and 0 <= t[1] < n:
                succ[(r, c)].append(t)
                pred[t].append((r, c))

    m = Model()

    # step[s, t] = 1 if the knight goes from square s straight to square t on the tour
    step = {(s, t): m.addVar(name=f"step_{s[0]}_{s[1]}_{t[0]}_{t[1]}", vtype="B")
            for s in squares for t in succ[s]}

    # first[s] = 1 if the tour starts on square s; last[s] = 1 if it ends there
    first = {s: m.addVar(name=f"first_{s[0]}_{s[1]}", vtype="B") for s in squares}
    last = {s: m.addVar(name=f"last_{s[0]}_{s[1]}", vtype="B") for s in squares}

    # move[s] = the move number at which the knight is on square s, from 0 to n*n-1
    move = {s: m.addVar(name=f"move_{s[0]}_{s[1]}", vtype="I", lb=0, ub=N - 1) for s in squares}

    # the tour starts on exactly one square and ends on exactly one square
    m.addCons(quicksum(first[s] for s in squares) == 1)
    m.addCons(quicksum(last[s] for s in squares) == 1)

    for s in squares:
        # every square except the last one is left by exactly one knight move
        m.addCons(quicksum(step[s, t] for t in succ[s]) == 1 - last[s])
        # every square except the first one is entered by exactly one knight move
        m.addCons(quicksum(step[u, s] for u in pred[s]) == 1 - first[s])

    # a knight move from s to t means t is the next move after s, so the move numbers increase along the tour;
    # this rules out cycles, so the moves form one open path that covers all squares
    for (s, t), b in step.items():
        m.addConsIndicator(move[t] - move[s] >= 1, binvar=b)

    # the output is the board of move numbers, indexed [row][column]
    board = [[move[(r, c)] for c in range(n)] for r in range(n)]
    return m, {"x": board}
