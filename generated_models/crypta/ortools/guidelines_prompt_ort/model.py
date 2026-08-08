
from ortools.sat.python import cp_model
import json

# Input data
addend1 = list("BAIJJAJIIAHFCFEBBJEA")
addend2 = list("DHFGABCDIDBIFFAGFEJE")
result = list("GJEGACDDHFAFJBFIHEEF")

# Reverse for column-wise addition (rightmost digit first)
add1_rev = list(reversed(addend1))
add2_rev = list(reversed(addend2))
res_rev = list(reversed(result))

# Model definition
model = cp_model.CpModel()

# Decision Variables: one for each letter A-J
letters = list("ABCDEFGHIJ")
letter_var = {}
for L in letters:
    letter_var[L] = model.NewIntVar(0, 9, L)

# All letters must have distinct digits
model.AddAllDifferent(letter_var.values())

# No leading zeros for the two addends and the result
model.Add(letter_var[addend1[0]] != 0)
model.Add(letter_var[addend2[0]] != 0)
model.Add(letter_var[result[0]] != 0)

# Carry variables for each column (0..20)
# c[0] is carry into rightmost column, c[20] is carry out of leftmost
c = [model.NewIntVar(0, 1, f"c{i}") for i in range(len(add1_rev) + 1)]
# Carry into rightmost and out of leftmost must be zero
model.Add(c[0] == 0)
model.Add(c[len(add1_rev)] == 0)

# Column-wise addition constraints
n = len(add1_rev)
for i in range(n):
    a = letter_var[add1_rev[i]]
    b = letter_var[add2_rev[i]]
    s = letter_var[res_rev[i]]
    # a + b + carry_in = s + 10 * carry_out
    model.Add(a + b + c[i] == s + 10 * c[i + 1])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        L: solver.Value(letter_var[L]) for L in letters
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
