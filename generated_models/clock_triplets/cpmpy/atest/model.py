from cpmpy import *
import json

# Parameters
n = 12  # Number of numbers on the clock face

# Decision variables
x = intvar(1, n, shape=n, name="x")
max_triplet_sum = intvar(3, 36, name="max_triplet_sum")  # Triplet sum ranges from 1+2+3=6 to 10+11+12=33

# Model
model = Model([
    AllDifferent(x),
    x[0] == 12  # First number must be 12
])

# Constraint: Each triplet sum is <= max_triplet_sum
for i in range(n):
    a = x[(i - 1) % n]
    b = x[i]
    c = x[(i + 1) % n]
    model += [a + b + c <= max_triplet_sum]

# Constraint: Ensure the maximum triplet sum is at most 21
model += [max_triplet_sum <= 21]

# Objective: Minimize the maximum triplet sum
model.minimize(max_triplet_sum)

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))