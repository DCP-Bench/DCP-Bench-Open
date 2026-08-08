import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Low Autocorrelation Binary Sequences
# - Binary sequence of length n=10, each element is +1 or -1
# - Using periodic (cyclic) boundary conditions
# - k-th autocorrelation: C_k = sum(S_i * S_{(i+k) mod n}) for i=0 to n-1
# - Objective: minimize E = sum(C_k^2) for k=1 to n-1

n = 10

# Step 2: Model with CPMpy
model = cp.Model()

# Decision variables: binary sequence with values +1 or -1
S = cp.intvar(-1, 1, shape=n, name="S")

# Constraint: each element must be either +1 or -1
for i in range(n):
    model += (S[i] == 1) | (S[i] == -1)

# Create auxiliary variables for autocorrelations C_k
# C_k = sum(S_i * S_{(i+k) mod n}) for i=0 to n-1
C = []
for k in range(1, n):  # k from 1 to n-1
    # Calculate C_k as sum of products
    terms = []
    for i in range(n):
        j = (i + k) % n
        terms.append(S[i] * S[j])
    
    # C_k can range from -n to +n
    C_k = cp.intvar(-n, n, name=f"C_{k}")
    model += C_k == cp.sum(terms)
    C.append(C_k)

# Create auxiliary variables for squared autocorrelations
C_squared = []
for k in range(len(C)):
    # C_k^2 can range from 0 to n^2
    C_k_sq = cp.intvar(0, n*n, name=f"C_{k+1}_squared")
    model += C_k_sq == C[k] * C[k]
    C_squared.append(C_k_sq)

# Objective: minimize E = sum(C_k^2)
E = cp.intvar(0, (n-1) * n * n, name="E")
model += E == cp.sum(C_squared)

# Symmetry breaking: fix first element to +1 to reduce search space
model += S[0] == 1

# Step 3: Solve and verify
model.minimize(E)

if model.solve():
    # Extract solution
    sequence = S.value().tolist()
    energy = E.value()
    
    # Verification: Independent calculation
    def verify_solution(seq):
        n = len(seq)
        autocorrelations = []
        for k in range(1, n):
            C_k = sum(seq[i] * seq[(i + k) % n] for i in range(n))
            autocorrelations.append(C_k)
        calculated_energy = sum(C_k * C_k for C_k in autocorrelations)
        return calculated_energy
    
    verified_energy = verify_solution(sequence)
    assert verified_energy == energy, f"Energy mismatch: {verified_energy} != {energy}"
    
    # Step 4: Output
    solution = {
        "sequence": sequence,
        "E": energy
    }
    
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))