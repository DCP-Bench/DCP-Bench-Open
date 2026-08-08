# Import libraries
from cpmpy import *
import json

# Input data
n = 12  # Number of pitch-classes

# Decision variables
x = intvar(0, n - 1, shape=n, name="x")  # The sequence of pitch-classes
diffs = intvar(1, n - 1, shape=n - 1, name="diffs")  # The intervals between consecutive pitch-classes

# Model
model = Model()

# x is a permutation of 0 to n-1
model += [AllDifferent(x)]

# diffs is the absolute difference between consecutive elements in x
for i in range(n - 1):
    model += [diffs[i] == abs(x[i + 1] - x[i])]

# diffs is a permutation of 1 to n-1
model += [AllDifferent(diffs)]

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist(), "diffs": diffs.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script