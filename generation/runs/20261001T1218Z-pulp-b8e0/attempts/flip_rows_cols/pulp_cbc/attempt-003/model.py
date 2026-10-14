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

    # Row i after the flips adds up to (sign of row i) * (sum_j matrix[i][j] * sign of column j).
    # The product of a sign and that sum is not linear. With unflipped_row_sum[i] the sum
    # when row i is not flipped (it lies between -reach and +reach), the row sum is
    # unflipped_row_sum if row i is not flipped and its negative if it is flipped, which these
    # four inequalities state exactly (reach is the largest value of the sum, so the
    # inequality of the branch not taken is always slack). Columns are treated the same way.
    # This uses the sums themselves instead of one product per matrix entry, which keeps the
    # relaxation small; the entries need not be written out at all.
    row_sum = []
    for i in range(rows):
        unflipped_row_sum = pulp.lpSum(matrix[i][j] * col_signs[j] for j in range(cols))
        reach = sum(abs(value) for value in matrix[i])
        # row i adds up to zero or more; its upper bound 300 is the reference's declared
        # domain of row and column sums (a problem constant)
        total_i = pulp.LpVariable(f"row_sum_{i}", 0, 300)
        problem += total_i >= unflipped_row_sum - 2 * reach * row_flip[i]
        problem += total_i <= unflipped_row_sum + 2 * reach * row_flip[i]
        problem += total_i >= -unflipped_row_sum - 2 * reach * (1 - row_flip[i])
        problem += total_i <= -unflipped_row_sum + 2 * reach * (1 - row_flip[i])
        row_sum.append(total_i)

    col_sum = []
    for j in range(cols):
        unflipped_col_sum = pulp.lpSum(matrix[i][j] * row_signs[i] for i in range(rows))
        reach = sum(abs(matrix[i][j]) for i in range(rows))
        # column j adds up to zero or more, and at most 300 (same declared domain)
        total_j = pulp.LpVariable(f"col_sum_{j}", 0, 300)
        problem += total_j >= unflipped_col_sum - 2 * reach * col_flip[j]
        problem += total_j <= unflipped_col_sum + 2 * reach * col_flip[j]
        problem += total_j >= -unflipped_col_sum - 2 * reach * (1 - col_flip[j])
        problem += total_j <= -unflipped_col_sum + 2 * reach * (1 - col_flip[j])
        col_sum.append(total_j)

    # The total of the whole matrix is the sum of its row sums and also the sum of its
    # column sums. It lies between 0 and 1000 (the reference's declared domain, a problem
    # constant) and is to be minimised.
    total_sum = pulp.LpVariable("total_sum", 0, 1000)
    problem += total_sum == pulp.lpSum(row_sum)
    problem += total_sum == pulp.lpSum(col_sum)
    problem += total_sum

    return problem, {"row_signs": row_signs, "col_signs": col_signs}
