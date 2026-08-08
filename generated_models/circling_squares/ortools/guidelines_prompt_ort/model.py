
from ortools.sat.python import cp_model
import json

# Create the CP-SAT model
model = cp_model.CpModel()

# Decision variables for the 10 squares (values between 1 and 99)
A = model.NewIntVar(1, 99, 'A')
B = model.NewIntVar(1, 99, 'B')
C = model.NewIntVar(1, 99, 'C')
D = model.NewIntVar(1, 99, 'D')
E = model.NewIntVar(1, 99, 'E')
F = model.NewIntVar(1, 99, 'F')
G = model.NewIntVar(1, 99, 'G')
H = model.NewIntVar(1, 99, 'H')
I = model.NewIntVar(1, 99, 'I')
K = model.NewIntVar(1, 99, 'K')

# Fix the given values: A=16, B=2, F=8, G=14
model.Add(A == 16)
model.Add(B == 2)
model.Add(F == 8)
model.Add(G == 14)

# All numbers must be different
model.AddAllDifferent([A, B, C, D, E, F, G, H, I, K])

# Create variables for squares
sq = {}
for var in [A, B, C, D, E, F, G, H, I, K]:
    sq[var.Name()] = model.NewIntVar(0, 99*99, f"sq_{var.Name()}")
    # Link square to the variable via multiplication
    model.AddMultiplicationEquality(sq[var.Name()], [var, var])

# List of variables in circular order
vars_in_circle = [A, B, C, D, E, F, G, H, I, K]

# Add the adjacency vs. opposite-sum-of-squares constraints
n = len(vars_in_circle)
for i in range(n):
    v1 = vars_in_circle[i]
    v2 = vars_in_circle[(i + 1) % n]
    opp1 = vars_in_circle[(i + 5) % n]
    opp2 = vars_in_circle[(i + 6) % n]
    # sq[v1] + sq[v2] == sq[opp1] + sq[opp2]
    model.Add(sq[v1.Name()] + sq[v2.Name()] == sq[opp1.Name()] + sq[opp2.Name()])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'A': solver.Value(A),
        'B': solver.Value(B),
        'C': solver.Value(C),
        'D': solver.Value(D),
        'E': solver.Value(E),
        'F': solver.Value(F),
        'G': solver.Value(G),
        'H': solver.Value(H),
        'I': solver.Value(I),
        'K': solver.Value(K)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
