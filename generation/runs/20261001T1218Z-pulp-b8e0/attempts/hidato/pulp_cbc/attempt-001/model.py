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

    problem = pulp.LpProblem("hidato", pulp.LpMinimize)  # satisfaction: no objective

    # put[r][c][k] = 1 if the cell in row r, column c holds the number k + 1. Every cell
    # holds one number and every number sits in one cell (all numbers are different and
    # there are as many numbers as cells). x reads the number of a cell back.
    put = pulp.LpVariable.dicts("put", (range(rows), range(cols), range(total)), cat="Binary")
    x = [[pulp.LpVariable(f"x_{r}_{c}", 1, total, cat="Integer") for c in range(cols)]
         for r in range(rows)]
    for r in range(rows):
        for c in range(cols):
            problem += pulp.lpSum(put[r][c][k] for k in range(total)) == 1
            problem += x[r][c] == pulp.lpSum((k + 1) * put[r][c][k] for k in range(total))
    for k in range(total):
        problem += pulp.lpSum(put[r][c][k] for r in range(rows) for c in range(cols)) == 1

    # the given numbers are fixed
    for r in range(rows):
        for c in range(cols):
            if puzzle[r][c] > 0:
                problem += put[r][c][puzzle[r][c] - 1] == 1

    # Consecutive numbers touch: if a cell holds the number k + 1 (k < total), one of its
    # (up to eight) neighbouring cells holds k + 2. A cell is not its own neighbour.
    for r in range(rows):
        for c in range(cols):
            neighbours = [(r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                          if (dr, dc) != (0, 0)
                          and 0 <= r + dr < rows and 0 <= c + dc < cols]
            for k in range(total - 1):
                problem += put[r][c][k] <= pulp.lpSum(put[nr][nc][k + 1]
                                                      for nr, nc in neighbours)

    return problem, {"x": x}
