
import cpmpy as cp
import json

# Data (optional)
arr = [72, 229, 107, 97, 110, 32, 75, 106, 101, 108, 108, 101, 114, 115, 116, 114, 97, 110, 100]
total = 666
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# b[i] = 1 means '+' before arr[i], b[i] = 0 means '-' before arr[i]
b = cp.boolvar(shape=len(arr), name="b")

# Constraints
# Sum of signed numbers equals total
model += (cp.sum([arr[i] * (2*b[i] - 1) for i in range(len(arr))]) == total)

# Objective (optional)
# No objective, just find any feasible solution

# Solve and print
if model.solve():
    result = [int(arr[i] * (2*int(b[i].value()) - 1)) for i in range(len(arr))]
    solution = {'result': result}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
