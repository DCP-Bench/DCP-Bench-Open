# Import libraries
from cpmpy import *
import json

# Parameters
n = 12  # Length of the magic sequence

# Decision Variables
x = intvar(0, n-1, shape=n, name="x")  # Magic sequence

# Model
model = Model()

# Constraint: for all i in 0 to n-1, the number i occurs exactly x_i times in the sequence
for i in range(n):
    model += sum(x == i) == x[i]

# Solve
model.solve()

# Print solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script