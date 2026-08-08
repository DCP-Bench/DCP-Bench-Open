
import cpmpy as cp
import json

n = 10

model = cp.Model()

# Decision variables
b = cp.boolvar(shape=n, name="b")
s = 2 * b - 1  # Convert 0/1 to -1/1

# Compute the energy E (periodic autocorrelation)
E = 0
for k in range(1, n):
    terms = []
    for i in range(n):
        next_i = (i + k) % n  # Periodic boundary condition
        terms.append(s[i] * s[next_i])
    Ck = cp.sum(terms)
    E += Ck * Ck

model.minimize(E)

# Solve and print
if model.solve():
    solution = {
        'sequence': s.value().tolist(),
        'E': int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
