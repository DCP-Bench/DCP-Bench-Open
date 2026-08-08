
from ortools.sat.python import cp_model
import json

# Number of people
n = 13
# Number of females (1s) and males (0s)
num_females = 9
num_males = 4

# Create the CP model
model = cp_model.CpModel()

# Decision variables: sequence[i] = 1 if female enters at position i, 0 if male
sequence = [model.NewBoolVar(f"seq_{i}") for i in range(n)]

# Constraint: exactly 9 females and 4 males
model.Add(sum(sequence) == num_females)

# Ensure the first person is male to avoid division by zero and infinite ratio
model.Add(sequence[0] == 0)

# For each prefix of the sequence, enforce females/males <= 7/3.
# Let F_j = sum(sequence[0..j]) and M_j = (j+1) - F_j.
# Constraint: F_j / M_j <= 7/3  <=> 3*F_j <= 7*M_j  <=> 10*F_j <= 7*(j+1)
for j in range(n):
    # sum of females in prefix 0..j
    prefix_females = sum(sequence[: j + 1])
    model.Add(10 * prefix_females <= 7 * (j + 1))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        "sequence": [solver.Value(sequence[i]) for i in range(n)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
