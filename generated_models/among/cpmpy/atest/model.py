from cpmpy import *
import json

# Parameters
n = 5  # Length of x
m = 3  # Number of values
v = [1, 5, 8]  # Values to be among in x

# Decision variables
x = intvar(0, 10, shape=n, name="x")  # Assuming values in x can be up to 10

# Model
model = Model()

# Requires exactly m variables in x to take one of the values in v
# Use logical OR to check if x[i] is in v
model += [sum([any([x[i] == val for val in v]) for i in range(n)]) == m]

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))