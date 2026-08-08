
import cpmpy as cp
import json

# Data
input_data = {
    "possible_assignments": [
        [1, 0, 1, 0, 0], # possible_assignments[i][j] is 1 if participant i is interested in car j, 0 otherwise
        [0, 0, 1, 1, 0],
        [1, 1, 1, 0, 1],
        [0, 1, 0, 1, 1],
        [1, 0, 0, 1, 0]
    ]
}
# End of data

possible = input_data["possible_assignments"]
n_participants = len(possible)
n_cars = len(possible[0]) if n_participants > 0 else 0

# Model definition
model = cp.Model()

# Decision Variables: assignments[i][j] is 1 if participant i assigned to car j, else 0
assignments = cp.boolvar(shape=(n_participants, n_cars), name="assignments")

# Constraints
# Only allow assignments where possible
for i in range(n_participants):
    for j in range(n_cars):
        if possible[i][j] == 0:
            model += (assignments[i, j] == 0)
# Each participant assigned to at most one car
for i in range(n_participants):
    model += cp.sum(assignments[i, :]) <= 1
# Each car assigned to at most one participant
for j in range(n_cars):
    model += cp.sum(assignments[:, j]) <= 1

# Objective: maximize total number of assignments
model.maximize(cp.sum(assignments))

# Solve and print
if model.solve():
    # Convert boolean values to 0/1 integers
    assignments_list = [[int(v) for v in row] for row in assignments.value().tolist()]
    solution = {'assignments': assignments_list}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
