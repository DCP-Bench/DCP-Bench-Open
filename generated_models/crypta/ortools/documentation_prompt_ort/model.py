from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Letters involved
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

# Create variables for each letter: digits 0-9
vars = {l: model.NewIntVar(0, 9, l) for l in letters}

# All letters must be distinct digits
model.AddAllDifferent(vars.values())

# The cryptarithmetic addition:
#   B A I J J A J I I A H F C F E B B J E A
# + D H F G A B C D I D B I F F A G F E J E
# -----------------------------------------
# = G J E G A C D D H F A F J B F I H E E F

# Represent the numbers as lists of letters (from left to right)
top = ['B', 'A', 'I', 'J', 'J', 'A', 'J', 'I', 'I', 'A', 'H', 'F', 'C', 'F', 'E', 'B', 'B', 'J', 'E', 'A']
bottom = ['D', 'H', 'F', 'G', 'A', 'B', 'C', 'D', 'I', 'D', 'B', 'I', 'F', 'F', 'A', 'G', 'F', 'E', 'J', 'E']
result = ['G', 'J', 'E', 'G', 'A', 'C', 'D', 'D', 'H', 'F', 'A', 'F', 'J', 'B', 'F', 'I', 'H', 'E', 'E', 'F']

# Length of numbers
n = len(top)  # 20 digits

# We will sum digit by digit from right to left with carry
carry = [model.NewIntVar(0, 2, f'carry_{i}') for i in range(n+1)]
# carry[n] is the carry out of the most significant digit (should be 0)
model.Add(carry[n] == 0)

# For each position from right to left
for i in range(n-1, -1, -1):
    t = vars[top[i]]
    b = vars[bottom[i]]
    r = vars[result[i]]
    # sum: t + b + carry[i+1] = r + 10 * carry[i]
    model.Add(t + b + carry[i+1] == r + carry[i] * 10)

# Leading digits of top, bottom, and result cannot be zero
model.Add(vars[top[0]] != 0)
model.Add(vars[bottom[0]] != 0)
model.Add(vars[result[0]] != 0)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {l: solver.Value(vars[l]) for l in letters}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")