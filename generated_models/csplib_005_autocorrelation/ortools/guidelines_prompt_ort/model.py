
from ortools.sat.python import cp_model
import json

# Input data
n = 10  # Length of the binary sequence

# Model definition
model = cp_model.CpModel()

# Decision Variables: sequence S[i] in {-1, 1}
S = [model.NewIntVar(-1, 1, f"S[{i}]") for i in range(n)]

# Autocorrelations C[k] for k = 1..n-1 (non-periodic)
C = {}
for k in range(1, n):
    # C_k ranges from -(n-k) to (n-k)
    C[k] = model.NewIntVar(-(n - k), n - k, f"C[{k}]")

# Products P[i,k] = S[i] * S[i+k]
P = {}
for k in range(1, n):
    for i in range(n - k):
        P[(i, k)] = model.NewIntVar(-1, 1, f"P[{i},{k}]")
        # Link product to S[i] * S[i+k]
        model.AddMultiplicationEquality(P[(i, k)], [S[i], S[i + k]])

# Define C[k] = sum_{i=0 to n-k-1} P[i,k]
for k in range(1, n):
    model.Add(C[k] == sum(P[(i, k)] for i in range(n - k)))

# Squared autocorrelations E_k = C[k]^2
E_k = {}
for k in range(1, n):
    # Max square is (n-k)^2
    max_sq = (n - k) * (n - k)
    E_k[k] = model.NewIntVar(0, max_sq, f"E_k[{k}]")
    # Enforce E_k = C[k] * C[k]
    model.AddMultiplicationEquality(E_k[k], [C[k], C[k]])

# Total energy E = sum_{k=1 to n-1} E_k
E = model.NewIntVar(0, sum((n - k) * (n - k) for k in range(1, n)), "E")
model.Add(E == sum(E_k[k] for k in range(1, n)))
model.Minimize(E)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        "sequence": [solver.Value(S[i]) for i in range(n)],
        "E": int(solver.ObjectiveValue())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
