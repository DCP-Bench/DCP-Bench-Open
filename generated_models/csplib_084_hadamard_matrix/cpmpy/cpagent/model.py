import cpmpy as cp
import numpy as np
import json

# Problem: 2cc Hadamard Matrix Legendre Pairs CSP
# For l=9, find sequences a and b of length l with values in {-1, +1}
# such that specific autocorrelation constraints are satisfied

# Problem parameters
l = 9  # odd positive integer
m = (l - 1) // 2  # m = (l-1)/2 = 4

# Step 1: Model with CPMpy
model = cp.Model()

# Decision variables: a_1, ..., a_l, b_1, ..., b_l
# All variables have domain {-1, +1}
a = cp.intvar(-1, 1, shape=l, name="a")
b = cp.intvar(-1, 1, shape=l, name="b")

# Domain constraints: variables can only be -1 or +1 (not 0)
for i in range(l):
    model += (a[i] == -1) | (a[i] == 1)
    model += (b[i] == -1) | (b[i] == 1)

# Linear constraints:
# c_{m+1}: a_1 + ... + a_l = 1
# c_{m+2}: b_1 + ... + b_l = 1
model += cp.sum(a) == 1
model += cp.sum(b) == 1

# Quadratic constraints:
# c_s: PAF(A, s) + PAF(B, s) = -2 for s = 1, ..., m
# where PAF(X, s) = sum_{i=1}^l x_i * x_{i+s} (indices taken mod l)
for s in range(1, m + 1):
    # PAF(A, s) = sum_{i=0}^{l-1} a[i] * a[(i + s) % l]
    paf_a = cp.sum([a[i] * a[(i + s) % l] for i in range(l)])
    
    # PAF(B, s) = sum_{i=0}^{l-1} b[i] * b[(i + s) % l]
    paf_b = cp.sum([b[i] * b[(i + s) % l] for i in range(l)])
    
    # Constraint: PAF(A, s) + PAF(B, s) = -2
    model += paf_a + paf_b == -2

# Step 2: Solve (this is a satisfaction problem, not optimization)
if model.solve():
    # Extract solution values
    a_solution = a.value()
    b_solution = b.value()
    
    # Convert to Python lists for JSON output
    a_list = a_solution.tolist() if hasattr(a_solution, 'tolist') else list(a_solution)
    b_list = b_solution.tolist() if hasattr(b_solution, 'tolist') else list(b_solution)
    
    # Output in required JSON format
    solution = {
        "a": a_list,
        "b": b_list
    }
    
    print(json.dumps(solution))
    
else:
    print(json.dumps({"error": "No solution found"}))