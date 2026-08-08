# Import libraries
from cpmpy import *
import json

# Parameters
n = 12  # Number of pitch-classes

# Decision Variables
x = intvar(0, n-1, shape=n, name="x")  # Sequence of pitch-classes
diffs = intvar(1, n-1, shape=n-1, name="diffs")  # Intervals between consecutive pitch-classes

# Model
model = Model()

# Constraint: x is a permutation of {0, 1, ..., n-1}
model += AllDifferent(x)

# Constraint: diffs are the absolute differences between consecutive elements in x
for i in range(n-1):
    model += diffs[i] == abs(x[i+1] - x[i])

# Constraint: diffs is a permutation of {1, 2, ..., n-1}
model += AllDifferent(diffs)

# Solve
model.solve()

# Print solution
solution = {
    "x": x.value().tolist(),
    "diffs": diffs.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script