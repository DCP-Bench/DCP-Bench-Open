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

    problem = pulp.LpProblem("hidato", pulp.LpMinimize)  # satisfaction: no objective

    # x[r][c] = the number in the cell; the given numbers are fixed
    x = [[pulp.LpVariable(f"x_{r}_{c}", 1, total, cat="Integer") for c in range(cols)]
         for r in range(rows)]
    given_at = {}  # number -> cell, for the given numbers
    for r, c in squares:
        if puzzle[r][c] > 0:
            problem += x[r][c] == puzzle[r][c]
            given_at[puzzle[r][c]] = (r, c)

    # the (up to eight) cells next to a cell
    def neighbours(r, c):
        return [(r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                if (dr, dc) != (0, 0) and 0 <= r + dr < rows and 0 <= c + dc < cols]

    # step[(p, q)] = 1 if the number k + 1 is in cell q right after the number k in cell p; a
    # step goes to a neighbouring cell. When an end of a step is a given number, the other end
    # holds the number next to it, so a step is left out when that cannot be: it needs the next
    # number not to be given in another cell (and, when both ends are given, to be next to it).
    def possible(p, q):
        given_p, given_q = puzzle[p[0]][p[1]], puzzle[q[0]][q[1]]
        if given_p > 0 and given_q > 0:
            return given_q == given_p + 1
        if given_p > 0:
            return given_p + 1 not in given_at and given_p < total
        if given_q > 0:
            return given_q - 1 not in given_at and given_q > 1
        return True

    step = {(p, q): pulp.LpVariable(f"step_{p[0]}_{p[1]}_{q[0]}_{q[1]}", cat="Binary")
            for p in squares for q in neighbours(*p) if possible(p, q)}

    # first[p] = 1 if p holds the number 1, last[p] = 1 if p holds the number `total`.
    first = {p: pulp.LpVariable(f"first_{p[0]}_{p[1]}", cat="Binary") for p in squares}
    last = {p: pulp.LpVariable(f"last_{p[0]}_{p[1]}", cat="Binary") for p in squares}
    problem += pulp.lpSum(first.values()) == 1
    problem += pulp.lpSum(last.values()) == 1

    for p in squares:
        r, c = p
        # Every cell but the one with the number 1 is entered by one step (from the cell with
        # the number before it), and every cell but the one with the last number is left by one
        # step (to the cell with the number after it).
        problem += pulp.lpSum(step[(q, p)] for q in neighbours(r, c) if (q, p) in step) \
            == 1 - first[p]
        problem += pulp.lpSum(step[(p, q)] for q in neighbours(r, c) if (p, q) in step) \
            == 1 - last[p]
        # the cell with the number 1 holds 1 and no other cell does; the cell with the last
        # number holds it and no other cell does
        problem += x[r][c] <= 1 + (total - 1) * (1 - first[p])
        problem += x[r][c] >= 2 - first[p]
        problem += x[r][c] >= total - (total - 1) * (1 - last[p])
        problem += x[r][c] <= total - 1 + last[p]

    # A step from p to q goes from the number k to the number k + 1. Following the steps from
    # the cell with the number 1 gives numbers that rise by one at every step, so the steps
    # cannot close into a cycle and all cells hold different numbers 1..total. Big-M: two
    # numbers differ by at most total - 1.
    for (p, q), s in step.items():
        problem += x[q[0]][q[1]] >= x[p[0]][p[1]] + 1 - total * (1 - s)
        problem += x[q[0]][q[1]] <= x[p[0]][p[1]] + 1 + (total - 2) * (1 - s)

    return problem, {"x": x}
