# Import libraries
from cpmpy import *
import json

# Parameters
n = 10  # Length of the binary sequence

# Decision Variables
sequence = intvar(-1, 1, shape=n, name="sequence")  # Binary sequence with values -1 and 1

# Ensure that the sequence only contains -1 or 1 (no 0)
model = Model([
    (sequence == -1) | (sequence == 1)
])

# Calculate autocorrelations and energy
C = []
for k in range(1, n):
    # Periodic autocorrelation
    C_k = sum(sequence[i] * sequence[(i + k) % n] for i in range(n))
    C.append(C_k)

# Energy E is the sum of squares of autocorrelations
E = sum(C_k ** 2 for C_k in C)

# Add E to the model for minimization
model.minimize(E)

# Solve
model.solve()

# Print
solution = {
    "sequence": sequence.value().tolist(),
    "E": E.value()
}
print(json.dumps(solution))
# End of CPMPy script