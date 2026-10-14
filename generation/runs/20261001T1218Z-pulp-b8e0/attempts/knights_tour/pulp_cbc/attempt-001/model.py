"""Knight's tour: a knight moves over an n x n chessboard and visits every square exactly
once, without having to return to its starting square. Number the squares 0..n*n-1 in the
order in which the knight visits them.

The model reports the board with the move number of every square.
"""
import pulp


def build(instance):
    n = instance["n"]  # board size
    cells = n * n  # the move numbers are 0..cells-1

    problem = pulp.LpProblem("knights_tour", pulp.LpMinimize)  # satisfaction: no objective

    # visit[r][c][k] = 1 if the knight is on square (r, c) at move k. Every square is
    # visited exactly once (one move number per square), and every move number is used once
    # (all numbers are different and there are as many numbers as squares). x reads the
    # move number of a square back.
    visit = pulp.LpVariable.dicts("visit", (range(n), range(n), range(cells)), cat="Binary")
    x = [[pulp.LpVariable(f"x_{r}_{c}", 0, cells - 1, cat="Integer") for c in range(n)]
         for r in range(n)]
    for r in range(n):
        for c in range(n):
            problem += pulp.lpSum(visit[r][c][k] for k in range(cells)) == 1
            problem += x[r][c] == pulp.lpSum(k * visit[r][c][k] for k in range(cells))
    for k in range(cells):
        problem += pulp.lpSum(visit[r][c][k] for r in range(n) for c in range(n)) == 1

    # the squares a knight can jump to from (r, c)
    jumps = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

    for r in range(n):
        for c in range(n):
            reachable = [(r + dr, c + dc) for dr, dc in jumps
                         if 0 <= r + dr < n and 0 <= c + dc < n]
            for k in range(cells):
                # after every move but the last, the knight jumps to a square numbered k + 1
                if k < cells - 1:
                    problem += visit[r][c][k] <= pulp.lpSum(visit[nr][nc][k + 1]
                                                            for nr, nc in reachable)
                # before every move but the first, the knight came from a square numbered k - 1
                if k > 0:
                    problem += visit[r][c][k] <= pulp.lpSum(visit[nr][nc][k - 1]
                                                            for nr, nc in reachable)

    return problem, {"x": x}
