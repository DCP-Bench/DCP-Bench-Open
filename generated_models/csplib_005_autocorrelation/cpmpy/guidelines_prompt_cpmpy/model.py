
import cpmpy as cp
import json

# Data
n = 10  # Length of the binary sequence
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# S[i] in {-1, +1}, we use IntVar(-1,1) and forbid 0
S = cp.intvar(-1, 1, shape=n, name="S")
model += [S[i] != 0 for i in range(n)]

# Compute autocorrelations C_k for k = 1..n-1 (non-periodic)
Cs = []
for k in range(1, n):
    # C_k = sum_{i=0 to n-k-1} S[i] * S[i+k]
    Cs.append(cp.sum([S[i] * S[i + k] for i in range(n - k)]))

# Objective: minimize E = sum_{k=1..n-1} C_k^2
E = cp.sum([C * C for C in Cs])
model.minimize(E)

# Solve and print
if model.solve():
    solution = {
        "sequence": [int(S[i].value()) for i in range(n)],
        "E": int(model.objective_value())
    }
    print(json.dumps(solution))
else:
    print("No solution found.")
