
import cpmpy as cp
import json

# Data
size = 10  # Number of marks on the Golomb ruler
# End of data

# Model definition
model = cp.Model()

# Upper bound for the last mark (length). A reasonable upper bound is chosen.
# This can be increased if needed, but keeps the search space manageable.
ub = 100

# Decision Variables
marks = cp.intvar(0, ub, shape=size, name="marks")  # marks[0] ... marks[size-1]

# Constraints
# 1) First mark is 0
model += (marks[0] == 0)

# 2) Marks are strictly increasing
model += cp.IncreasingStrict(marks)

# 3) All pairwise differences are distinct (Golomb property)
diffs = []
for i in range(size):
    for j in range(i + 1, size):
        diffs.append(marks[j] - marks[i])
# Differences must be at least 1 and all different
model += (cp.AllDifferent(diffs))
# enforce positive differences (redundant with IncreasingStrict but explicit)
model += [d >= 1 for d in diffs]

# 4) Symmetry breaking: fix orientation so the second mark is not larger than half the length
#    2 * marks[1] <= marks[-1]
model += (2 * marks[1] <= marks[-1])

# Objective: minimize the length (last mark)
length = marks[-1]
model.minimize(length)

# Solve and print
if model.solve():
    solution = {
        'marks': marks.value().tolist(),
        'length': int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
