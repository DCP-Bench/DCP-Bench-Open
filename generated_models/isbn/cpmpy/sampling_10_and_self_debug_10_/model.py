
import cpmpy as cp
import json

# Data: provide the 13-length ISBN list here.
# Use -1 for unknown digits. For example:
# isbn_input = [9,7,8,0,3,0,6,4,0,0,0,0,-1]
# The judge/test harness may replace this list with the actual instance.
isbn_input = [-1] * 13
# End of data

# Model definition
model = cp.Model()

# Decision Variables: 13 digits, each between 0 and 9
isbn = cp.intvar(0, 9, shape=13, name="isbn")

# Constraints
# 1) Enforce given digits
for i, d in enumerate(isbn_input):
    if d != -1:
        # If a provided digit is out of range [0,9], this will simply be unsatisfiable.
        model += (isbn[i] == int(d))

# 2) ISBN-13 must start with 978 or 979
model += (isbn[0] == 9)
model += (isbn[1] == 7)
model += ((isbn[2] == 8) | (isbn[2] == 9))

# 3) Check digit constraint for ISBN-13:
#    Multiply first 12 digits alternately by 1 and 3 (starting with 1),
#    sum them, check = (10 - (sum % 10)) % 10, and isbn[12] == check.
weights = [1 if i % 2 == 0 else 3 for i in range(12)]
weighted_sum = cp.sum([weights[i] * isbn[i] for i in range(12)])
# Use modulo and arithmetic to compute check digit
model += (isbn[12] == ((10 - (weighted_sum % 10)) % 10))

# Solve and print
if model.solve():
    solution = {'isbn': isbn.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
