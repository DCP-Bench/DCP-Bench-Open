"""Hidato: a grid is partly filled with numbers. Fill the empty cells so that the grid holds
each of the numbers 1..(rows * columns) once and every number k is next to the number k + 1,
horizontally, vertically or diagonally (the numbers form a path through the grid).

The model reports the filled grid.
"""
import pulp


def build(instance):
    puzzle = instance["puzzle"]  # puzzle[r][c] > 0 is a given number, 0 means empty
    rows, cols = len(puzzle), len(puzzle[0])
    total = rows * cols  # the numbers are 1..total
    squares = [(r, c) for r in range(rows) for c in range(cols)]
    givens = [((r, c), puzzle[r][c]) for r, c in squares if puzzle[r][c] > 0]

    problem = pulp.LpProblem("hidato", pulp.LpMinimize)  # satisfaction: no objective

    # Which numbers a cell can hold. Consecutive numbers touch, so from number k to number g
    # the path makes |k - g| steps of one cell (diagonals included): two cells holding k and g
    # are at most |k - g| apart in that sense (the larger of the row and column distances).
    # A cell can only hold k if this holds for every given number; a given cell holds its own
    # number only. This follows from the rules and only leaves out impossible placements.
    def apart(p, q):
        return max(abs(p[0] - q[0]), abs(p[1] - q[1]))

    def possible(p, k):
        if puzzle[p[0]][p[1]] > 0:
            return k == puzzle[p[0]][p[1]]
        return all(apart(p, q) <= abs(k - g) for q, g in givens)

    # put[(p, k)] = 1 if cell p holds the number k, for the possible placements only. Every cell
    # holds one number and every number is in one cell (all numbers are different and there are
    # as many numbers as cells). x reads the number of a cell back.
    put = {(p, k): pulp.LpVariable(f"put_{p[0]}_{p[1]}_{k}", cat="Binary")
           for p in squares for k in range(1, total + 1) if possible(p, k)}
    x = [[pulp.LpVariable(f"x_{r}_{c}", 1, total, cat="Integer") for c in range(cols)]
         for r in range(rows)]
    for p in squares:
        options = [k for k in range(1, total + 1) if (p, k) in put]
        problem += pulp.lpSum(put[(p, k)] for k in options) == 1
        problem += x[p[0]][p[1]] == pulp.lpSum(k * put[(p, k)] for k in options)
    for k in range(1, total + 1):
        problem += pulp.lpSum(put[(p, k)] for p in squares if (p, k) in put) == 1

    # the given numbers are fixed
    for p, g in givens:
        problem += put[(p, g)] == 1

    # the (up to eight) cells next to a cell
    def neighbours(r, c):
        return [(r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                if (dr, dc) != (0, 0) and 0 <= r + dr < rows and 0 <= c + dc < cols]

    # Consecutive numbers touch: if a cell holds k (k < total), a neighbouring cell holds k + 1;
    # and if it holds k (k > 1), a neighbouring cell holds k - 1. (The second follows from the
    # first once every number is placed; it is stated as well because it tightens the
    # relaxation.)
    for (p, k), var in put.items():
        near = neighbours(*p)
        if k < total:
            problem += var <= pulp.lpSum(put[(q, k + 1)] for q in near if (q, k + 1) in put)
        if k > 1:
            problem += var <= pulp.lpSum(put[(q, k - 1)] for q in near if (q, k - 1) in put)

    return problem, {"x": x}
