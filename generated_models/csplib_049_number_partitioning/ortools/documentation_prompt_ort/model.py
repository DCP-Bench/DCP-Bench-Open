from ortools.sat.python import cp_model
import json

# Input data
n = 12  # The number N

# Model definition
model = cp_model.CpModel()

# Decision variables: x[i] = 1 if number i+1 is in set A, 0 if in set B
x = [model.NewBoolVar(f'x_{i+1}') for i in range(n)]

# Constraints

# 1) A and B have the same cardinality
model.Add(sum(x) == n // 2)

# 2) Sum of numbers in A = sum of numbers in B
# sum of numbers in A = sum of numbers in B = total_sum / 2
total_sum = n * (n + 1) // 2
model.Add(sum((i + 1) * x[i] for i in range(n)) == total_sum // 2)

# 3) Sum of squares of numbers in A = sum of squares of numbers in B
# sum of squares in A = sum of squares in B = total_squares / 2
total_squares = sum((i + 1) ** 2 for i in range(n))
model.Add(sum(((i + 1) ** 2) * x[i] for i in range(n)) == total_squares // 2)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    A = [i + 1 for i in range(n) if solver.Value(x[i]) == 1]
    B = [i + 1 for i in range(n) if solver.Value(x[i]) == 0]
    solution = {
        'A': A,
        'B': B
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")