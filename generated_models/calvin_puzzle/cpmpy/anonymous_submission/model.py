from cpmpy import *
import json
import numpy as np

# Parameters
n = 5  # Size of the grid

# Decision Variables
x = intvar(1, n*n, shape=(n, n), name="x")  # Grid values
rows = intvar(0, n-1, shape=n*n, name="rows")  # Row positions for each number
cols = intvar(0, n-1, shape=n*n, name="cols")  # Column positions for each number

# Model
model = Model()

# Constraint: All values must be distinct and cover 1 to n^2
model += AllDifferent(x.flat)

# Channeling constraints: Connect grid values to position variables
for i in range(n):
    for j in range(n):
        for k in range(n*n):
            model += (x[i,j] == k+1).implies((rows[k] == i) & (cols[k] == j))

# Movement constraints between consecutive numbers
for k in range(1, n*n):
    # Movement Type I: horizontal/vertical with 3-square distance (2-square gap)
    move_type1 = (
        ((rows[k-1] == rows[k]) & (abs(cols[k-1] - cols[k]) == 3)) |
        ((cols[k-1] == cols[k]) & (abs(rows[k-1] - rows[k]) == 3))
    )
    
    # Movement Type II: diagonal with 2-square distance (1-square gap)
    move_type2 = (abs(rows[k-1] - rows[k]) == 2) & (abs(cols[k-1] - cols[k]) == 2)
    
    model += move_type1 | move_type2

# Solve
model.solve()

# Print solution
solution = {
    "x": x.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script