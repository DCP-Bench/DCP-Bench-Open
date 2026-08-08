
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: digits d[0]..d[9], each 0..9
d = cp.intvar(0, 9, shape=10, name="d")

# Constraints
model += cp.AllDifferent(d)        # use each digit 0..9 exactly once
model += d[0] != 0                 # leading digit must not be 0 (10-digit number)

# For each prefix length n (1..10), the integer formed by first n digits is divisible by n
for n in range(1, 11):
    # value of prefix of length n: sum_{i=0..n-1} d[i] * 10^(n-1-i)
    coeffs = [10 ** (n - 1 - i) for i in range(n)]
    val = cp.sum([coeffs[i] * d[i] for i in range(n)])
    model += (val % n) == 0

# Solve and print
if model.solve():
    digits = d.value().tolist()
    number = int("".join(str(x) for x in digits))
    solution = {'number': number}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
