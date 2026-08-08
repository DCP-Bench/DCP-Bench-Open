# ------------------------------------------------------------
#  Autocorrelation minimisation (aperiodic / open boundary)
#  n = 10  –  Google OR-Tools CP-SAT model
# ------------------------------------------------------------

from ortools.sat.python import cp_model
import json

# ------------------------------------------------------------
# Input data (immutable)
# ------------------------------------------------------------

n = 10  # Length of the binary sequence
boundary_condition = "open"  # fixed for this instance; left as a parameter for reuse

# ------------------------------------------------------------
# Model creation
# ------------------------------------------------------------

model = cp_model.CpModel()

# Decision variables: sequence elements S_i ∈ {+1, -1}
S = [
    model.NewIntVarFromDomain(cp_model.Domain.FromValues([-1, 1]), f"S[{i}]")
    for i in range(n)
]

# Optional symmetry-breaking: Fix first symbol to +1 so that the all-negated
# sequence is not explored separately.  Harmless for correctness, accelerates search.
model.Add(S[0] == 1)

# Auxiliary variables for autocorrelations and their squares
C = []          # autocorrelation values C_k
C_sq = []       # squares C_k^2

# Helper container for products S_i * S_{i+k}
# C_k = Σ_{i=0}^{n−k−1}  (S_i · S_{i+k})
for k in range(1, n):
    # Create the autocorrelation variable C_k
    max_abs = n - k                     # |C_k| ≤ n-k
    C_k = model.NewIntVar(-max_abs, max_abs, f"C[{k}]")
    C.append(C_k)

    # Build products for the sum defining C_k
    products = []
    upper_i = n - k - 1 if boundary_condition == "open" else n - 1

    # Iterate over i according to the boundary condition
    if boundary_condition == "open":
        index_range = range(0, n - k)
    else:  # cyclic / periodic
        index_range = range(n)

    for i in index_range:
        j = (i + k) % n
        p = model.NewIntVarFromDomain(cp_model.Domain.FromValues([-1, 1]), f"P_{i}_{k}")
        # p = S_i * S_j
        model.AddMultiplicationEquality(p, [S[i], S[j]])
        products.append(p)

    # Sum of the products equals C_k
    model.Add(C_k == sum(products))

    # Square of C_k:  C_k_sq = C_k * C_k
    C_k_sq = model.NewIntVar(0, max_abs * max_abs, f"C_sq[{k}]")
    model.AddMultiplicationEquality(C_k_sq, [C_k, C_k])
    C_sq.append(C_k_sq)

# Energy variable: E = Σ C_k^2
E_max = sum((n - k) ** 2 for k in range(1, n))
E = model.NewIntVar(0, E_max, "E")
model.Add(E == sum(C_sq))

# Objective: minimise E
model.Minimize(E)

# ------------------------------------------------------------
# Solver
# ------------------------------------------------------------

solver = cp_model.CpSolver()

# Tighten search a bit – will solve instantly for n = 10 but the parameters
# help if re-used for larger instances.
solver.parameters.max_time_in_seconds = 30.0
solver.parameters.num_search_workers = 8

status = solver.Solve(model)

# ------------------------------------------------------------
# Output
# ------------------------------------------------------------

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    sequence = [int(solver.Value(var)) for var in S]
    E_val = int(solver.Value(E))
    print(json.dumps({"sequence": sequence, "E": E_val}))
else:
    raise RuntimeError("No feasible solution found.")
