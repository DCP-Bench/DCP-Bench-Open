
import cpmpy as cp
import json

n = 10  # Length of the binary sequence

# Model definition
model = cp.Model()

# Decision Variables
s_bool = cp.boolvar(shape=n)
s = 2 * s_bool - 1  # Convert to -1 or 1

# Compute autocorrelations and energy
autocorrelations = []
for k in range(1, n):
    terms = []
    for i in range(n - k):
        terms.append(s[i] * s[i + k])
    Ck = cp.sum(terms)
    autocorrelations.append(Ck)
    
E = cp.sum([ck**2 for ck in autocorrelations])

# Objective: minimize energy
model.minimize(E)

# Solve and print
if model.solve():
    # Extract sequence values and compute energy
    s_val = s_bool.value()
    sequence = (2 * s_val - 1).tolist()
    E_val = model.objective_value()
    solution = {
        'sequence': sequence,
        'E': int(E_val)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
