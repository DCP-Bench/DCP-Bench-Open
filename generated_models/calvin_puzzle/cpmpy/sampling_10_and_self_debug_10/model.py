
import cpmpy as cp
import json

n = 5

# Model definition
model = cp.Model()

# Variables
# x[i,j] = the number placed at position (i,j), from 1 to n^2
x = cp.intvar(1, n*n, shape=(n, n), name="x")

# pos[num] = (row, col) position of number num in the grid
pos_r = cp.intvar(0, n-1, shape=n*n, name="pos_r")
pos_c = cp.intvar(0, n-1, shape=n*n, name="pos_c")

# Constraints

# 1) All numbers 1..n^2 appear exactly once in the grid
model += cp.AllDifferent(x)

# 2) Link position variables with x variables:
# For each number k in 1..n^2, pos_r[k-1], pos_c[k-1] is the position of k in x
# We enforce that x[pos_r[k-1], pos_c[k-1]] == k
for k in range(1, n*n+1):
    model += x[pos_r[k-1], pos_c[k-1]] == k

# 3) All positions pos_r and pos_c are valid indices (already domain defined)

# 4) All positions for numbers 1..n^2 are all different (no two numbers share the same cell)
# We can enforce that the pairs (pos_r[k], pos_c[k]) are all different
# To do this, we create a single integer representing the position: pos_r * n + pos_c
pos_flat = [pos_r[i]*n + pos_c[i] for i in range(n*n)]
model += cp.AllDifferent(pos_flat)

# 5) Movement constraints between consecutive numbers k and k+1:
# If next number is placed vertically or horizontally, distance must be exactly 3 squares away (gap 2)
# If next number is placed diagonally, distance must be exactly 2 squares away (gap 1)
# So for each k in 1..n^2-1:
# Let dr = abs(pos_r[k] - pos_r[k-1])
# Let dc = abs(pos_c[k] - pos_c[k-1])
# Then either (dr == 3 and dc == 0) or (dr == 0 and dc == 3) or (dr == 2 and dc == 2)

for k in range(n*n-1):
    dr = cp.abs(pos_r[k+1] - pos_r[k])
    dc = cp.abs(pos_c[k+1] - pos_c[k])
    # Create boolean variables for each condition
    cond_vert = (dr == 3) & (dc == 0)
    cond_horiz = (dr == 0) & (dc == 3)
    cond_diag = (dr == 2) & (dc == 2)
    model += cond_vert | cond_horiz | cond_diag

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
