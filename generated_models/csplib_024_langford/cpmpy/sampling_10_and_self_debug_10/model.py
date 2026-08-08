
import cpmpy as cp
import json

# Data
k = 4  # Number of sets
n = 4  # Numbers from 1 to n

# Model definition
model = cp.Model()

# We have k sets of numbers 1..n, so total length is k*n
length = k * n

# Decision variables
# solution[i] = number at position i (0-based indexing)
solution = cp.intvar(1, n, shape=length, name="solution")

# position[m][j] = position of the j-th occurrence of number m+1 (0-based)
# m in [0..n-1], j in [0..k-1]
position = cp.intvar(0, length - 1, shape=(n, k), name="position")

# Constraints

# 1) The positions for each number m must be all different
for m in range(n):
    model += cp.AllDifferent(position[m])

# 2) The positions for all numbers must be all different (no two numbers share the same position)
# Flatten position array and enforce all different
model += cp.AllDifferent(position.flat)

# 3) Link solution and position variables:
# For each number m+1 and each occurrence j, solution[position[m][j]] == m+1
for m in range(n):
    for j in range(k):
        model += solution[position[m][j]] == m + 1

# 4) The spacing constraints:
# For each number m+1, the occurrences must be spaced m+1 apart
# That is, for each j in [0..k-2]:
# position[m][j+1] == position[m][j] + m + 1
for m in range(n):
    for j in range(k - 1):
        model += position[m][j + 1] == position[m][j] + (m + 1)

# 5) The positions must be in increasing order for each number (already implied by above, but we add for clarity)
for m in range(n):
    for j in range(k - 1):
        model += position[m][j] < position[m][j + 1]

# Solve and print
if model.solve():
    solution_list = solution.value().tolist()
    position_list = position.value().tolist()
    # Convert position to 1-based indexing for output (optional, but problem states positions)
    position_1based = [[pos + 1 for pos in occ] for occ in position_list]
    solution_dict = {
        'position': position_1based,
        'solution': solution_list
    }
    print(json.dumps(solution_dict, indent=4))
else:
    print("No solution found.")
