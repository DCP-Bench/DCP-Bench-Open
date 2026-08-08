
from ortools.sat.python import cp_model
import json

# Given set A of ten integers
A = [81, 21, 79, 4, 29, 70, 28, 20, 14, 7]

# Create the CP-SAT model
model = cp_model.CpModel()

# Decision variables: in_S[i] = 1 if A[i] is in subset S, in_T[i] = 1 if A[i] is in subset T
in_S = [model.NewBoolVar(f"in_S[{i}]") for i in range(len(A))]
in_T = [model.NewBoolVar(f"in_T[{i}]") for i in range(len(A))]

# Constraint: S and T are disjoint
for i in range(len(A)):
    model.Add(in_S[i] + in_T[i] <= 1)

# Constraint: S and T are non-empty
model.Add(sum(in_S) >= 1)
model.Add(sum(in_T) >= 1)

# Constraint: sums of elements in S and T are equal
model.Add(
    sum(A[i] * in_S[i] for i in range(len(A)))
    == sum(A[i] * in_T[i] for i in range(len(A)))
)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'in_S': [solver.Value(in_S[i]) for i in range(len(A))],
        'in_T': [solver.Value(in_T[i]) for i in range(len(A))]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
