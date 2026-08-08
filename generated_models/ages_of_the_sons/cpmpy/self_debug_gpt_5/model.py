
import cpmpy as cp
import json

# Data (compute ambiguous sums given product 36)
product = 36
triples = []
sum_counts = {}
for x in range(1, product+1):
    if product % x != 0:
        continue
    for y in range(x, product+1):
        if (product // x) % y != 0:
            continue
        z = product // (x*y)
        if y <= z and x*y*z == product:
            s = x + y + z
            triples.append((x, y, z, s))
            sum_counts[s] = sum_counts.get(s, 0) + 1

ambiguous_sums = sorted([s for s, c in sum_counts.items() if c > 1])

# Model definition
model = cp.Model()

# Decision Variables (ordered from oldest to youngest)
A = cp.intvar(1, product, shape=3, name="A")

# Constraints
# Order ages from oldest to youngest
model += (A[0] >= A[1])
model += (A[1] >= A[2])

# Product of ages is 36
model += (A[0] * A[1] * A[2] == product)

# The mathematician couldn't deduce from the sum alone -> sum must be ambiguous
model += cp.InDomain(cp.sum(A), ambiguous_sums)

# "The oldest son has blue eyes" implies there is a unique oldest age
model += (A[0] > A[1])

# Objective (optional): choose the lexicographically largest (prefer larger oldest),
# this selects the classic solution (9,2,2) among the two possibilities.
model.maximize(A[0]*100 + A[1]*10 + A[2])

# Solve and print
if model.solve():
    solution = {
        'A1': int(A[0].value()),
        'A2': int(A[1].value()),
        'A3': int(A[2].value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
