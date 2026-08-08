
import cpmpy as cp
import json

# Data
n = 10
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# Represent the sequence bits as integer variables taking values in {-1, 1}
sequence = cp.intvar(-1, 1, shape=n, name="sequence")

# Constraints
# Each element must be either -1 or 1
model += (sequence != 0)

# Compute autocorrelations C_k for k=1..n-1 with periodic boundary conditions
C = []
for k in range(1, n):
    # sum over i=0..n-1 of S_i * S_{(i+k) mod n}
    terms = [sequence[i] * sequence[(i + k) % n] for i in range(n)]
    Ck = cp.sum(terms)
    C.append(Ck)

# Objective: minimize sum of squares of autocorrelations
E = cp.sum([c * c for c in C])
model.minimize(E)

# Solve and print
if model.solve():
    solution = {'sequence': sequence.value().tolist(), 'E': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
