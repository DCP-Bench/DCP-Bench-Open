
import cpmpy as cp
import json

# Data (optional)
# Input ISBN-13 with -1 for unknown digits
input_isbn = [9, 7, 8, 0, 3, 0, 6, 4, 0, 6, 1, 5, -1]
# End of data

# Model definition
model = cp.Model()

# Decision Variables
isbn = cp.intvar(0, 9, shape=13, name="isbn")

# Constraints
bad_input = False
if not isinstance(input_isbn, list) or len(input_isbn) != 13:
    bad_input = True
else:
    for d in input_isbn:
        if not (d == -1 or (isinstance(d, int) and 0 <= d <= 9)):
            bad_input = True
            break

if bad_input:
    model += (0 == 1)  # Unsatisfiable if bad input
else:
    # Apply known digits
    for i, d in enumerate(input_isbn):
        if d != -1:
            model += (isbn[i] == d)

    # ISBN-13 must start with 978 or 979
    model += (isbn[0] == 9)
    model += (isbn[1] == 7)
    model += ((isbn[2] == 8) | (isbn[2] == 9))

    # Check digit constraint:
    # Let s be the weighted sum of the first 12 digits (weights 1,3,... starting with 1)
    s = cp.sum([isbn[i] * (1 if i % 2 == 0 else 3) for i in range(12)])

    # Enforce (s + isbn[12]) % 10 == 0 by introducing k with s + isbn[12] == 10*k
    k = cp.intvar(0, 23, name="k")  # Upper bound sufficient: (max s 216 + 9) / 10 <= 23
    model += (s + isbn[12] == 10 * k)

# Solve and print
if model.solve():
    solution = {'isbn': isbn.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
