"""Quasigroup completion: complete a partly filled N x N table so that every row and every
column holds each of the numbers 1..N exactly once (a Latin square).

The model reports the completed table.
"""
import pulp


def build(instance):
    n = instance["N"]  # size of the quasigroup
    start = instance["start"]  # start[i][j] = given number, or 0 for an empty cell

    problem = pulp.LpProblem("quasigroup_completion", pulp.LpMinimize)  # satisfaction: no objective

    # put[i][j][v] = 1 if the cell in row i, column j holds the number v + 1.
    # The cell holds exactly one number, and puzzle reads that number back.
    put = pulp.LpVariable.dicts("put", (range(n), range(n), range(n)), cat="Binary")
    puzzle = [[pulp.LpVariable(f"puzzle_{i}_{j}", 1, n, cat="Integer") for j in range(n)]
              for i in range(n)]
    for i in range(n):
        for j in range(n):
            problem += pulp.lpSum(put[i][j][v] for v in range(n)) == 1
            problem += puzzle[i][j] == pulp.lpSum((v + 1) * put[i][j][v] for v in range(n))

    # the filled cells of the start table keep their numbers
    for i in range(n):
        for j in range(n):
            if start[i][j] != 0:
                problem += put[i][j][start[i][j] - 1] == 1

    for v in range(n):
        # each row holds each number once
        for i in range(n):
            problem += pulp.lpSum(put[i][j][v] for j in range(n)) == 1
        # each column holds each number once
        for j in range(n):
            problem += pulp.lpSum(put[i][j][v] for i in range(n)) == 1

    return problem, {"puzzle": puzzle}
