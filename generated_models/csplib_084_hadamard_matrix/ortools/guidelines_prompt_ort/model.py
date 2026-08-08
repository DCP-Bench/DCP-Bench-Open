
from ortools.sat.python import cp_model
import json

# Input data
l = 9  # Value of l (must be an odd positive integer)
m = (l - 1) // 2  # Number of quadratic constraints

# Model definition
model = cp_model.CpModel()

# Decision Variables: a[i] and b[i] in {-1, +1}
a = [model.NewIntVar(-1, 1, f"a_{i+1}") for i in range(l)]
b = [model.NewIntVar(-1, 1, f"b_{i+1}") for i in range(l)]

# Quadratic constraints via product variables
# For each shift s = 1..m, enforce PAF(A,s) + PAF(B,s) == -2
for s in range(1, m + 1):
    # Collect product terms for A and B
    pA = []
    pB = []
    for i in range(l):
        j = (i + s) % l
        # product variable for a[i] * a[j]
        p_ai_aj = model.NewIntVar(-1, 1, f"pA_{s}_{i}")
        model.AddMultiplicationEquality(p_ai_aj, [a[i], a[j]])
        pA.append(p_ai_aj)
        # product variable for b[i] * b[j]
        p_bi_bj = model.NewIntVar(-1, 1, f"pB_{s}_{i}")
        model.AddMultiplicationEquality(p_bi_bj, [b[i], b[j]])
        pB.append(p_bi_bj)
    # Sum of autocorrelations for shift s
    model.Add(sum(pA) + sum(pB) == -2)

# Linear constraints: sums of a's and b's equal 1
model.Add(sum(a) == 1)
model.Add(sum(b) == 1)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'a': [solver.Value(a[i]) for i in range(l)],
        'b': [solver.Value(b[i]) for i in range(l)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
