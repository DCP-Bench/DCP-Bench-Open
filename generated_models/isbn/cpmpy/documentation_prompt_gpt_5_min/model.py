
import cpmpy as cp
import json
import sys

# Read input from stdin if provided. Expect either a JSON list like [9,7,8,-1,...]
# or a JSON object like {"isbn": [9,7,8,-1,...]}
data = None
s = sys.stdin.read().strip()
if s:
    try:
        parsed = json.loads(s)
        if isinstance(parsed, dict) and "isbn" in parsed:
            data = parsed["isbn"]
        elif isinstance(parsed, list):
            data = parsed
    except Exception:
        data = None

# Fallback example if no input given
if data is None:
    # Example with unknowns after 978
    data = [9, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]

# Validate input length
if not isinstance(data, list) or len(data) != 13:
    print("No solution found.")
    sys.exit(0)

given = data

# Model definition
model = cp.Model()

# Decision Variables: 13 digits, each 0..9
isbn_vars = cp.intvar(0, 9, shape=13, name="isbn")

# Apply known digits (where given != -1)
for i, val in enumerate(given):
    if isinstance(val, int) and val != -1:
        model += (isbn_vars[i] == val)

# ISBN-13 must start with 978 or 979: enforce first two digits 9 and 7, and third in {8,9}
model += (isbn_vars[0] == 9)
model += (isbn_vars[1] == 7)
# third digit must be 8 or 9
model += cp.InDomain(isbn_vars[2], [8, 9])

# Compute checksum for first 12 digits: multiply alternately by 1 and 3 starting with 1
weights = [1 if i % 2 == 0 else 3 for i in range(12)]
checksum_expr = cp.sum([weights[i] * isbn_vars[i] for i in range(12)])

# Check digit constraint: (checksum + last_digit) % 10 == 0
model += ((checksum_expr + isbn_vars[12]) % 10 == 0)

# Solve and print
if model.solve():
    solution = {'isbn': isbn_vars.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
