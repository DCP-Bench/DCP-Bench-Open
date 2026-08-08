
import cpmpy as cp
import json

# Data
n = 10
# End of data

# Model definition
model = cp.Model()

# Decision variables: sequence of length n with values -1 or +1
sequence = cp.intvar(-1, 1, shape=n, name="sequence")

# Constraints: each element must be either -1 or 1 (exclude 0)
for i in range(n):
    model += cp.InDomain(sequence[i], [-1, 1])

# Calculate autocorrelations Ck for k=1..n-1 (non-periodic)
C = []
for k in range(1, n):
    terms = [sequence[i] * sequence[i + k] for i in range(n - k)]
    Ck = cp.sum(terms)
    C.append(Ck)

# Energy E = sum of squares of autocorrelations
E = cp.sum([c * c for c in C])

# Objective: minimize E
model.minimize(E)

# Solve and print
if model.solve():
    solution = {'sequence': sequence.value().tolist(), 'E': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
