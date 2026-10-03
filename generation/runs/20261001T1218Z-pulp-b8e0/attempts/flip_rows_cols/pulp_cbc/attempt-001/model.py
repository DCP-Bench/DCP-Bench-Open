"""Flip rows and columns: given a matrix of numbers, the sign of any whole row or column may be
flipped. Choose the flips so that every row and every column sums to zero or more, and the
total of the whole matrix is as small as possible.

The model reports the sign (+1 or -1) applied to each row and to each column.
"""
import pulp


def build(instance):
    matrix = instance["input_matrix"]
    rows = len(matrix)
    cols = len(matrix[0])

    problem = pulp.LpProblem("flip_rows_cols", pulp.LpMinimize)

    # row_flip[i] = 1 if row i is flipped, col_flip[j] = 1 if column j is flipped;
    # the sign applied to a row or column is 1 - 2 * flip (+1 unflipped, -1 flipped).
    row_flip = [pulp.LpVariable(f"row_flip_{i}", cat="Binary") for i in range(rows)]
    col_flip = [pulp.LpVariable(f"col_flip_{j}", cat="Binary") for j in range(cols)]
    row_signs = [1 - 2 * f for f in row_flip]
    col_signs = [1 - 2 * f for f in col_flip]

    # The entry (i, j) becomes matrix[i][j] * row sign * col sign. The product of the two
    # signs is -1 exactly when one of the two (not both) is flipped, so it is
    # 1 - 2 * flipped[i][j] with flipped[i][j] = row_flip[i] XOR col_flip[j].
    flipped = [[pulp.LpVariable(f"flipped_{i}_{j}", cat="Binary") for j in range(cols)]
               for i in range(rows)]
    for i in range(rows):
        for j in range(cols):
            problem += flipped[i][j] >= row_flip[i] - col_flip[j]
            problem += flipped[i][j] >= col_flip[j] - row_flip[i]
            problem += flipped[i][j] <= row_flip[i] + col_flip[j]
            problem += flipped[i][j] <= 2 - row_flip[i] - col_flip[j]
    entry = [[matrix[i][j] * (1 - 2 * flipped[i][j]) for j in range(cols)] for i in range(rows)]

    # every row sum is at least 0; its upper bound 300 is the reference's declared domain
    # of row and column sums (a problem constant)
    for i in range(rows):
        row_sum = pulp.lpSum(entry[i])
        problem += row_sum >= 0
        problem += row_sum <= 300
    # every column sum is at least 0, and at most 300 (same declared domain)
    for j in range(cols):
        col_sum = pulp.lpSum(entry[i][j] for i in range(rows))
        problem += col_sum >= 0
        problem += col_sum <= 300

    # the total of the whole matrix, between 0 and 1000 (the reference's declared domain,
    # a problem constant), is to be minimised
    total_sum = pulp.lpSum(entry[i][j] for i in range(rows) for j in range(cols))
    problem += total_sum >= 0
    problem += total_sum <= 1000
    problem += total_sum

    return problem, {"row_signs": row_signs, "col_signs": col_signs}
