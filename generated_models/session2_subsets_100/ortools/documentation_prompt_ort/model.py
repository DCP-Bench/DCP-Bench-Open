from ortools.sat.python import cp_model
import json

# Given set A
A = [81, 21, 79, 4, 29, 70, 28, 20, 14, 7]

# Model definition
model = cp_model.CpModel()

n = len(A)

# Decision variables: in_S[i] = 1 if A[i] in S, else 0
in_S = [model.NewBoolVar(f'in_S_{i}') for i in range(n)]
# Decision variables: in_T[i] = 1 if A[i] in T, else 0
in_T = [model.NewBoolVar(f'in_T_{i}') for i in range(n)]

# Constraint: S and T are disjoint
for i in range(n):
    model.Add(in_S[i] + in_T[i] <= 1)

# Constraint: S and T are non-empty
model.Add(sum(in_S) >= 1)
model.Add(sum(in_T) >= 1)

# Constraint: sum of elements in S equals sum of elements in T
sum_S = sum(in_S[i] * A[i] for i in range(n))
sum_T = sum(in_T[i] * A[i] for i in range(n))
model.Add(sum_S == sum_T)

# No objective, just find any feasible solution
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'in_S': [solver.Value(var) for var in in_S],
        'in_T': [solver.Value(var) for var in in_T]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")