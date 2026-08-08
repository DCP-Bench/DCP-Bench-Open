
import cpmpy as cp
import json

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
# End of data

m = len(input_matrix)
n = len(input_matrix[0])

# Model definition
model = cp.Model()

# Decision Variables
# r[i] == 1 means the i-th row is flipped (boolean)
r = cp.boolvar(shape=m, name="r")
# c[j] == 1 means the j-th column is flipped (boolean)
c = cp.boolvar(shape=n, name="c")

# b[i,j] == 1 iff cell (i,j) is flipped an odd number of times (r XOR c)
b = cp.boolvar(shape=(m, n), name="b")

# t[i,j] is the signed value of cell (i,j) after applying flips
# Bounds: cell values after flipping are either input or -input, so bounds are within max_abs
max_abs = max(abs(val) for row in input_matrix for val in row)
t = cp.intvar(-max_abs, max_abs, shape=(m, n), name="t")

# Constraints
# Link b with r and c: b[i,j] == r[i] XOR c[j]
for i in range(m):
    for j in range(n):
        model += (b[i, j] == (r[i] ^ c[j]))  # boolean equality

# Compute signed cell values linearly: t = input - 2 * input * b
# When b=0 -> t = input; when b=1 -> t = input - 2*input = -input
for i in range(m):
    for j in range(n):
        val = input_matrix[i][j]
        model += (t[i, j] == val - 2 * val * b[i, j])

# Row and column sums must be >= 0
for i in range(m):
    model += cp.sum(t[i, :]) >= 0

for j in range(n):
    model += cp.sum(t[:, j]) >= 0

# Objective: minimize overall sum
model.minimize(cp.sum(t))

# Solve and print
if model.solve():
    r_vals = r.value().tolist()
    c_vals = c.value().tolist()
    # Convert booleans (0/1) to signs (1/-1): sign = 1 - 2*flip
    row_signs = [int(1 - 2 * int(bv)) for bv in r_vals]
    col_signs = [int(1 - 2 * int(bv)) for bv in c_vals]
    solution = {'row_signs': row_signs, 'col_signs': col_signs}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
