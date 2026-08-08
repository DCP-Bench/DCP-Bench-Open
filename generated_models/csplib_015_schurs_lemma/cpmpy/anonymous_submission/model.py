# Import libraries
from cpmpy import *
import json

# Parameters
n = 13  # Number of balls
c = 3   # Number of boxes

# Decision Variables
balls = intvar(1, c, shape=n, name="balls")  # Assignment of balls to boxes (1-3)

# Model
model = Model()

# Constraint: for any x+y=z, not all three balls in the same box
for x in range(1, n+1):
    for y in range(1, n+1):
        z = x + y
        if z <= n:
            for box in range(1, c+1):
                model += sum([balls[x-1] == box, balls[y-1] == box, balls[z-1] == box]) <= 2

# Solve
model.solve()

# Print solution
solution = {
    "balls": balls.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script