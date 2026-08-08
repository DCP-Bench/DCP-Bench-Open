# Import libraries
from cpmpy import *
import json

# Parameters
n = 10  # Length of the binary sequence

# Decision Variables
sequence = intvar(-1, 1, shape=n, name="sequence")  # Binary sequence (+1 or -1)
E = intvar(0, (n-1)*n**2, name="E")  # Energy value to minimize

# Model
model = Model()

# Constraint to ensure sequence values are either +1 or -1
model += [abs(sequence[i]) == 1 for i in range(n)]

# Calculate autocorrelations C_k for periodic boundary conditions
C = []
for k in range(1, n):
    C_k = sum(sequence[i] * sequence[(i+k) % n] for i in range(n))
    C.append(C_k)

# Calculate energy E as sum of squares of autocorrelations
model += E == sum([ck**2 for ck in C])

# Objective: minimize E
model.minimize(E)

# Solve
model.solve()

# Print solution
solution = {
    "sequence": sequence.value().tolist(),
    "E": E.value()
}
print(json.dumps(solution))
# End of CPMPy script