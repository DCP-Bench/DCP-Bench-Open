
import cpmpy as cp
import json

# Data
arr = [72, 229, 107, 97, 110, 32, 75, 106, 101, 108, 108, 101, 114, 115, 116, 114, 97, 110, 100]
total = 666
# End of data

# Model definition
model = cp.Model()

# Decision Variables
n = len(arr)
# sign variables in {-1, 1} (use intvar with exclusion of 0)
sign = cp.intvar(-1, 1, shape=n, name="sign")
# result variables are the signed values of arr elements
max_a = max(arr)
result = cp.intvar(-max_a, max_a, shape=n, name="result")

# Constraints
# Exclude 0 so sign is either -1 or 1
model += [sign[i] != 0 for i in range(n)]
# Link result to sign * arr[i]
model += [result[i] == arr[i] * sign[i] for i in range(n)]
# Sum constraint
model += cp.sum([result[i] for i in range(n)]) == total

# Solve and print
if model.solve():
    solution = {'result': result.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
