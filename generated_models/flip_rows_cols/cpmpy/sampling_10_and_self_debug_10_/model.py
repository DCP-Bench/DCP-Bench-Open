
import cpmpy as cp
import json
import numpy as np

# Data
input_matrix = [
    [33, 30, 10, -6, 18, -7, -11, 23, -6],
    [16, -19, 9, -26, -8, -19, -8, -21, -14],
    [17, 12, -14, 31, -30, 13, -13, 19, 16],
    [-6, -11, 1, 17, -12, -4, -7, 14, -21],
    [18, -31, 34, -22, 17, -19, 20, 24, 6],
    [33, -18, 17, -15, 31, -5, 3, 27, -3],
    [-18, -20, -18, 31, 6, 4, -2, -12, 24],
    [27, 14, 4, -29, -3, 5, -29, 8, -12],
    [-15, -7, -23, 23, -9, -8, 6, 8, -12],
    [33, -23, -19, -4, -8, -7, 11, -12, 31],
    [-20, 19, -15, -30, 11, 32, 7, 14, -5],
    [-23, 18, -32, -2, -31, -7, 8, 24, 16],
    [32, -4, -10, -14, -6, -1, 0, 23, 23],
    [25, 0, -23, 22, 12, 28, -27, 15, 4],
    [-30, -13, -16, -3, -3, -32, -3, 27, -31],
    [22, 1, 26, 4, -2, -13, 26, 17, 14],
    [-9, -18, 3, -20, -27, -32, -11, 27, 13],
    [-17, 33, -7, 19, -32, 13, -31, -2, -24],
    [-31, 27, -31, -29, 15, 2, 29, -15, 33],
    [-18, -23, 15, 28, 0, 30, -4, 12, -32],
    [-3, 34, 27, -25, -18, 26, 1, 34, 26],
    [-21, -31, -10, -13, -30, -17, -12, -26, 31],
    [23, -31, -19, 21, -17, -10, 2, -23, 23],
    [-3, 6, 0, -3, -32, 0, -10, -25, 14],
    [-19, 9, 14, -27, 20, 15, -5, -27, 18],
    [11, -6, 24, 7, -17, 26, 20, -31, -25],
    [-25, 4, -16, 30, 33, 23, -4, -4, 23]
]
A = np.array(input_matrix, dtype=int)
n_rows, n_cols = A.shape
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# Use boolean variables and map to -1/1 via 2*b - 1 to avoid zero.
r_b = cp.boolvar(shape=n_rows, name="r_b")
c_b = cp.boolvar(shape=n_cols, name="c_b")
r_sign_expr = 2 * r_b - 1  # expressions yielding -1 or 1
c_sign_expr = 2 * c_b - 1

# Constraints
# For each row i: sum_j r_i * c_j * A[i][j] >= 0
for i in range(n_rows):
    row_terms = [(r_sign_expr[i] * c_sign_expr[j] * int(A[i, j])) for j in range(n_cols)]
    model += cp.sum(row_terms) >= 0

# For each column j: sum_i r_i * c_j * A[i][j] >= 0
for j in range(n_cols):
    col_terms = [(r_sign_expr[i] * c_sign_expr[j] * int(A[i, j])) for i in range(n_rows)]
    model += cp.sum(col_terms) >= 0

# Objective: minimize total sum after flips
all_terms = [(r_sign_expr[i] * c_sign_expr[j] * int(A[i, j])) for i in range(n_rows) for j in range(n_cols)]
objective = cp.sum(all_terms)
model.minimize(objective)

# Solve and print
if model.solve():
    # Evaluate the sign expressions to get -1/1 lists
    r_vals = (r_sign_expr).value().tolist()
    c_vals = (c_sign_expr).value().tolist()
    # Convert any boolean-ish or numpy ints to Python ints
    row_signs = [int(x) for x in r_vals]
    col_signs = [int(x) for x in c_vals]

    solution = {'row_signs': row_signs, 'col_signs': col_signs}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
