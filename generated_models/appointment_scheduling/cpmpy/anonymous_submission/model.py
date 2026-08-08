from cpmpy import *
import json

# Input data
m = [
    [1, 1, 1, 1],
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 1]
]  # Matrix representing the free-busy schedules

# Decision Variables
x = intvar(0, 1, shape=(4,4), name="x")  # Assignment matrix (people x slots)

# Model
model = Model()

# Constraint: Each person is assigned to exactly one slot
for i in range(4):
    model += sum(x[i]) == 1

# Constraint: Each slot has exactly one person
for j in range(4):
    model += sum(x[:,j]) == 1

# Constraint: People can only be assigned to slots where they are free
for i in range(4):
    for j in range(4):
        model += (x[i,j] == 1).implies(m[i][j] == 1)

# Solve
model.solve()

# Print solution with boolean values
solution = {
    "x": [[bool(val) for val in row] for row in x.value().tolist()]
}
print(json.dumps(solution))
# End of CPMPy script