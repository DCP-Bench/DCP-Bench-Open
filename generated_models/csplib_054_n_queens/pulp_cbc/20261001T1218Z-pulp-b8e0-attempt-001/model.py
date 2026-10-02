"""N queens: place n queens on an n x n chessboard so that no two queens are on
the same row, column or diagonal.

queens[r] is the column (1..n) of the queen in row r.
"""
import pulp


def build(instance):
    n = instance["n"]  # board size and number of queens

    problem = pulp.LpProblem("n_queens", pulp.LpMinimize)

    # on[r][c] = 1 if there is a queen on row r, column c (columns are numbered 1..n)
    on = [[pulp.LpVariable(f"on_{r}_{c}", cat="Binary") for c in range(1, n + 1)]
          for r in range(n)]

    # queens[r] = the column of the queen in row r (declared output), a bounded
    # integer tied to the 0/1 board by equality
    queens = [pulp.LpVariable(f"queens_{r}", 1, n, cat="Integer") for r in range(n)]

    # one queen in every row, and queens reads its column back
    for r in range(n):
        problem += pulp.lpSum(on[r]) == 1
        problem += queens[r] == pulp.lpSum((c + 1) * on[r][c] for c in range(n))

    # at most one queen in a column; as n queens are placed, exactly one
    for c in range(n):
        problem += pulp.lpSum(on[r][c] for r in range(n)) <= 1

    # at most one queen on each diagonal running down to the right (column - row constant)
    for d in range(-(n - 1), n):
        problem += pulp.lpSum(on[r][r + d] for r in range(n) if 0 <= r + d < n) <= 1

    # at most one queen on each diagonal running down to the left (column + row constant)
    for s in range(2 * n - 1):
        problem += pulp.lpSum(on[r][s - r] for r in range(n) if 0 <= s - r < n) <= 1

    return problem, {"queens": queens}
