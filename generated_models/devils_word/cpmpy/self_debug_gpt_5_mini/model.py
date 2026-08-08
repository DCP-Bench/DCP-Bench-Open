
import cpmpy as cp
import json

# Data
arr = [72, 229, 107, 97, 110, 32, 75, 106, 101, 108, 108, 101, 114, 115, 116, 114, 97, 110, 100]
total = 666
# End of data

# Model definition
model = cp.Model()

n = len(arr)
sum_arr = sum(arr)

# Decision Variables
# b[i] = 1 means +arr[i], b[i] = 0 means -arr[i]
b = cp.boolvar(shape=n, name="b")
# result variables: signed values for each element
result_vars = cp.intvar(-sum_arr, sum_arr, shape=n, name="result")

# Constraints
for i in range(n):
    # result[i] == arr[i] * (2*b[i] - 1)  -> either +arr[i] or -arr[i]
    model += (result_vars[i] == arr[i] * (2 * b[i] - 1))

# Sum of signed values equals the target total
model += cp.sum(result_vars) == total

# Solve and print
if model.solve():
    solution = {'result': [int(x) for x in result_vars.value().tolist()]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
