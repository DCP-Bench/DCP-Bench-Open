
import cpmpy as cp
import json

# Data (optional)
size = 10  # Number of marks on the Golomb ruler
# End of data

# Helper: triangular number T(n) = n*(n+1)//2
def triangular(n):
    return (n * (n + 1)) // 2

# Model definition
model = cp.Model()

# Decision Variables
# Upper bound heuristic: m^2 is a common constructive upper bound for Golomb rulers
UB = size * size
marks = cp.intvar(0, UB, shape=size, name="marks")

# Constraints
# First mark at 0, strictly increasing marks
model += (marks[0] == 0)
model += cp.IncreasingStrict(marks)

# Prefix lower bounds using triangular numbers (symmetry breaking and pruning)
for i in range(size):
    model += (marks[i] >= triangular(i))

# All pairwise differences must be distinct
diffs = [marks[j] - marks[i] for i in range(size) for j in range(i + 1, size)]
model += cp.AllDifferent(diffs)

# Break reflection symmetry: first gap <= last gap
model += (marks[1] - marks[0] <= marks[-1] - marks[-2])

# Objective (optional)
model.minimize(marks[-1])

# Solve and print
if model.solve():
    solution = {
        'marks': marks.value().tolist(),
        'length': int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
