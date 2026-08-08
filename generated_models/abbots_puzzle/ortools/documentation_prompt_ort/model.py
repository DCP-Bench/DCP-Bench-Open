from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Decision Variables
# Number of men, women, and children
men = model.NewIntVar(0, 100, 'men')
women = model.NewIntVar(0, 100, 'women')
children = model.NewIntVar(0, 100, 'children')

# Constraints
# Total people is 100
model.Add(men + women + children == 100)

# Total bushels is 100
# Each man gets 3 bushels, each woman 2, each child 0.5
model.Add(3 * men + 2 * women + (children / 2) == 100)

# There are five times as many women as men
model.Add(women == 5 * men)

# Since children/2 must be integer, children must be even
# We can enforce children to be even by children % 2 == 0
# OR we can multiply the whole equation by 2 to avoid fractions
# Let's multiply the bushel constraint by 2 to avoid fractions:
model.ClearConstraints()
model.Add(men + women + children == 100)
model.Add(6 * men + 4 * women + children == 200)
model.Add(women == 5 * men)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'men': solver.Value(men),
        'women': solver.Value(women),
        'children': solver.Value(children)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")