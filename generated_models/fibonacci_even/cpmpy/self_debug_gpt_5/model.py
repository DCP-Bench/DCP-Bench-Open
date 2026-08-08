
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Parameters
N = 32  # Number of Fibonacci terms to consider (up to 4,000,000)

# Decision Variables
f = cp.intvar(0, 4000000, shape=N, name="f")  # Fibonacci terms, bounded by 4,000,000
res = cp.intvar(0, 10000000, name="res")      # Sum of even-valued terms

# Constraints
# Initialize the first two terms
model += (f[0] == 1)
model += (f[1] == 2)

# Fibonacci recurrence
for i in range(2, N):
    model += (f[i] == f[i-1] + f[i-2])

# Sum of even-valued terms (every 3rd term starting from index 1 is even)
even_indices = list(range(1, N, 3))
model += (res == cp.sum([f[i] for i in even_indices]))

# Solve and print
if model.solve():
    solution = {'res': int(res.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
