
import cpmpy as cp
import json

# Data
n = 10  # Length of the binary sequence
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# b_i in {0,1} -> sequence value s_i = 2*b_i - 1 in {-1,1}
b = cp.intvar(0, 1, shape=n, name="b")

# We'll build pairwise products p_{i,j} for all required pairs (open boundary).
# For each lag k (1..n-1) we compute C_k = sum_{i=0}^{n-k-1} s_i * s_{i+k}
C_vars = []
T_vars = []  # squares of C_k via table constraint

# Helper containers for p and and-variables (not needed in solution output but for constraints)
for k in range(1, n):
    pairs_p = []
    for i in range(0, n - k):
        j = i + k
        # and_ij = b_i & b_j (as intvar 0/1)
        and_ij = cp.intvar(0, 1, name=f"and_{i}_{j}")
        # p_ij = s_i * s_j in {-1,1}
        p_ij = cp.intvar(-1, 1, name=f"p_{i}_{j}")
        # Linearize AND:
        model += (and_ij <= b[i])
        model += (and_ij <= b[j])
        model += (and_ij >= b[i] + b[j] - 1)
        # p = 4*and - 2*b_i - 2*b_j + 1  (since s = 2*b - 1)
        model += (p_ij == 4 * and_ij - 2 * b[i] - 2 * b[j] + 1)
        pairs_p.append(p_ij)

    # C_k bounds: sum of (n-k) items each in {-1,1}
    m = n - k
    Ck = cp.intvar(-m, m, name=f"C_{k}")
    model += (Ck == cp.sum(pairs_p))
    C_vars.append(Ck)

    # Square variable tk
    tk = cp.intvar(0, m * m, name=f"t_{k}")
    # Table to force tk == Ck^2 by enumerating all possible (Ck, tk) pairs
    table = [[v, v * v] for v in range(-m, m + 1)]
    model += cp.Table([Ck, tk], table)
    T_vars.append(tk)

# Objective: minimize sum of squares of autocorrelations
model.minimize(cp.sum(T_vars))

# Solve and print
if model.solve():
    b_vals = b.value().tolist()
    sequence = [2 * int(x) - 1 for x in b_vals]  # map 0->-1, 1->1
    solution = {'sequence': sequence}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
