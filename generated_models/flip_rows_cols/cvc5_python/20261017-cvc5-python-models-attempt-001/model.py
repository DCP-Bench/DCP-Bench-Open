# Flip rows and columns of a matrix of positive and negative numbers so that every
# row and every column has a non-negative sum, minimising the overall sum.
# Output: row_signs (one -1/1 per row) and col_signs (one -1/1 per column).
import cvc5.pythonic as cz


def build(instance):
    matrix = instance["input_matrix"]
    n = len(matrix)
    m = len(matrix[0])

    # Boolean flip flags: True means the row (column) sign is -1.
    rb = cz.Bools([f"rb{i}" for i in range(n)])
    cb = cz.Bools([f"cb{j}" for j in range(m)])

    # The value of entry (i, j) after flipping is a[i][j] when both signs agree and
    # -a[i][j] when they differ.
    def entry(i, j):
        a = matrix[i][j]
        return cz.If(cz.Xor(rb[i], cb[j]), -a, a)

    constraints = []

    # Every row and every column sums to a positive number or zero.
    # Rows:
    for i in range(n):
        constraints.append(cz.Sum([entry(i, j) for j in range(m)]) >= 0)
    # Columns:
    for j in range(m):
        constraints.append(cz.Sum([entry(i, j) for i in range(n)]) >= 0)

    # Overall sum of the flipped matrix, to be minimised.
    total = cz.Sum([entry(i, j) for i in range(n) for j in range(m)])

    row_signs = [cz.If(rb[i], -1, 1) for i in range(n)]
    col_signs = [cz.If(cb[j], -1, 1) for j in range(m)]

    return constraints, {"row_signs": row_signs, "col_signs": col_signs}, ("minimize", total)
