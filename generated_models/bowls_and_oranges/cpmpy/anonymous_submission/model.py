# Import libraries
from cpmpy import *
import json

# Decision Variables
x = intvar(1, 40, shape=9, name="x")  # Positions of the oranges (bowl numbers)

# Model
model = Model()

# Constraint: all oranges are in different bowls and in increasing order
model += AllDifferent(x)
model += [x[i] < x[i+1] for i in range(8)]

# Constraint: no three oranges form an arithmetic progression
for i in range(9):
    for j in range(i+1, 9):
        for k in range(j+1, 9):
            model += (x[j] - x[i] != x[k] - x[j])  # Direct difference comparison

# Solve
model.solve()

# Print solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script