"""Calvin's puzzle: fill an n by n grid with the numbers 1..n*n so that each next number
sits exactly three squares away horizontally or vertically, or exactly two squares away
diagonally, from the previous one.

The model reports the completed grid x.
"""
import pulp


def build(instance):
    n = instance["n"]
    cells = [(i, j) for i in range(n) for j in range(n)]
    last = n * n  # the numbers placed are 1..n*n

    problem = pulp.LpProblem("calvin_puzzle", pulp.LpMinimize)  # satisfaction: no objective

    # x[i][j] is the number written in square (i, j)
    x = [[pulp.LpVariable(f"x_{i}_{j}", 1, last, cat="Integer") for j in range(n)]
         for i in range(n)]

    # The allowed moves from the problem statement: three squares along a row or column
    # (Movement Type I), or two squares along a diagonal (Movement Type II).
    steps = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]

    def moves(cell):
        i, j = cell
        return [(i + a, j + b) for a, b in steps if 0 <= i + a < n and 0 <= j + b < n]

    # follow[c, d] = 1 if the number after the one in square c is written in square d.
    # Successor arcs over the legal moves only, rather than a number-by-square
    # assignment, keep the program at one binary per legal move.
    follow = {(c, d): pulp.LpVariable(f"follow_{c[0]}_{c[1]}_{d[0]}_{d[1]}", cat="Binary")
              for c in cells for d in moves(c)}
    out_arcs = {c: [] for c in cells}
    in_arcs = {c: [] for c in cells}
    for (c, d), var in follow.items():
        out_arcs[c].append(var)
        in_arcs[d].append(var)

    # every square has at most one next number and at most one previous number,
    # and the n*n numbers are joined by n*n - 1 moves
    for c in cells:
        problem += pulp.lpSum(out_arcs[c]) <= 1
        problem += pulp.lpSum(in_arcs[c]) <= 1
    problem += pulp.lpSum(follow.values()) == last - 1

    # when square d follows square c, its number is one more than the number in c;
    # last is the largest possible gap between two numbers, so the constraint is
    # inactive when the move is not taken
    for (c, d), var in follow.items():
        problem += x[d[0]][d[1]] - x[c[0]][c[1]] - 1 <= last * (1 - var)
        problem += x[d[0]][d[1]] - x[c[0]][c[1]] - 1 >= -last * (1 - var)

    # the square with no previous number holds the number 1. Since numbers rise by one
    # along every move, no moves can close a cycle, so the moves form one path from that
    # square through every square and the grid holds 1..n*n exactly once each.
    for c in cells:
        problem += x[c[0]][c[1]] <= 1 + (last - 1) * pulp.lpSum(in_arcs[c])

    return problem, {"x": x}
