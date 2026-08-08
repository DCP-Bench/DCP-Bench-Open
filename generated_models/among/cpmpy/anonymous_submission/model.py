# Import libraries
from cpmpy import *
import json

# Parameters
n = 5  # Length of x
m = 3  # Number of values
v = [1, 5, 8]  # Values to be among in x

# Decision Variables
x = intvar(0, 10, shape=n, name="x")  # Array x with values between 0 and 10

# Model
model = Model()

# Exactly m variables in x must take one of the values in v
model += sum([sum([x[i] == val for val in v]) >= 1 for i in range(n)]) == m

# Solve
model.solve()

# Print solution
solution = {
    "x": x.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script