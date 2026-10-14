"""Knight's tour: a knight moves over an n x n chessboard and visits every square exactly
once, without having to return to its starting square. Number the squares 0..n*n-1 in the
order in which the knight visits them.

The model reports the board with the move number of every square.
"""
import pulp


def build(instance):
    n = instance["n"]  # board size
    cells = n * n  # the move numbers are 0..cells-1
    squares = [(r, c) for r in range(n) for c in range(n)]

    problem = pulp.LpProblem("knights_tour", pulp.LpMinimize)  # satisfaction: no objective

    # the squares a knight can jump to from (r, c)
    jumps = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

    def reachable(r, c):
        return [(r + dr, c + dc) for dr, dc in jumps if 0 <= r + dr < n and 0 <= c + dc < n]

    # x[r][c] = move number of the square
    x = [[pulp.LpVariable(f"x_{r}_{c}", 0, cells - 1, cat="Integer") for c in range(n)]
         for r in range(n)]

    # jump[(p, q)] = 1 if the knight jumps from square p straight to square q
    jump = {(p, q): pulp.LpVariable(f"jump_{p[0]}_{p[1]}_{q[0]}_{q[1]}", cat="Binary")
            for p in squares for q in reachable(*p)}

    # first[p] = 1 if p is the square of move 0, last[p] = 1 if p is the square of the last
    # move (cells - 1).
    first = {p: pulp.LpVariable(f"first_{p[0]}_{p[1]}", cat="Binary") for p in squares}
    last = {p: pulp.LpVariable(f"last_{p[0]}_{p[1]}", cat="Binary") for p in squares}
    problem += pulp.lpSum(first.values()) == 1
    problem += pulp.lpSum(last.values()) == 1

    for p in squares:
        r, c = p
        # Every square but the first is entered by one jump, and every square but the last is
        # left by one jump (the move after it, and the move before it, are one knight jump away).
        problem += pulp.lpSum(jump[(q, p)] for q in reachable(r, c)) == 1 - first[p]
        problem += pulp.lpSum(jump[(p, q)] for q in reachable(r, c)) == 1 - last[p]
        # the first square has move number 0 and no other has; the last has the move number
        # cells - 1 and no other has
        problem += x[r][c] <= (cells - 1) * (1 - first[p])
        problem += x[r][c] >= 1 - first[p]
        problem += x[r][c] >= (cells - 1) * last[p]
        problem += x[r][c] <= cells - 2 + last[p]

    # A jump from p to q goes from move k to move k + 1. Every square is visited once: following
    # the jumps from the first square gives move numbers that rise by one at every jump, so the
    # jumps cannot close into a cycle and the squares are numbered 0, 1, 2, ... without gaps.
    # Big-M: the move numbers differ by at most cells - 1.
    for (p, q), j in jump.items():
        problem += x[q[0]][q[1]] >= x[p[0]][p[1]] + 1 - cells * (1 - j)
        problem += x[q[0]][q[1]] <= x[p[0]][p[1]] + 1 + (cells - 2) * (1 - j)

    return problem, {"x": x}
