
import cpmpy as cp
import json

# Data
size = 10  # Number of marks on the Golomb ruler
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# marks: positions of the marks on the ruler, 0 = a1 < a2 < ... < a_m
# The first mark is fixed at 0
marks = cp.intvar(0, 1000, shape=size, name="marks")
model += (marks[0] == 0)

# The marks must be strictly increasing
for i in range(size - 1):
    model += (marks[i] < marks[i + 1])

# Differences: all pairwise differences a_j - a_i for 1 <= i < j <= m
num_diffs = size * (size - 1) // 2
diffs = cp.intvar(1, 1000, shape=num_diffs, name="diffs")

# Fill diffs with all differences a_j - a_i (i < j)
diff_index = 0
for i in range(size):
    for j in range(i + 1, size):
        model += (diffs[diff_index] == marks[j] - marks[i])
        diff_index += 1

# All differences must be distinct
model += cp.AllDifferent(diffs)

# Symmetry breaking: first difference < last difference
model += (marks[1] - marks[0] < marks[size - 1] - marks[size - 2])

# Objective: minimize the length of the ruler (last mark)
length = marks[size - 1]
model.minimize(length)

# Solve and print
if model.solve():
    solution = {'marks': marks.value().tolist(), 'length': int(length.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
