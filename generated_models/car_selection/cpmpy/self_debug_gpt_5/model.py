
import cpmpy as cp
import json

# Data (optional)
input_data = {
    "possible_assignments": [
        [1, 0, 1, 0, 0],  # participant 0
        [0, 0, 1, 1, 0],  # participant 1
        [1, 1, 1, 0, 1],  # participant 2
        [0, 1, 0, 1, 1],  # participant 3
        [1, 0, 0, 1, 0]   # participant 4
    ]
}
# End of data

# Extract data
possible = input_data["possible_assignments"]
n_participants = len(possible)
n_cars = len(possible[0]) if n_participants > 0 else 0

# Model definition
model = cp.Model()

# Decision Variables
# assignments[i][j] = 1 if participant i is assigned to car j, else 0
assignments = cp.boolvar(shape=(n_participants, n_cars), name="assignments")

# Constraints
# 1) Each participant is assigned to at most one car
for i in range(n_participants):
    model += (cp.sum(assignments[i, :]) <= 1)

# 2) Each car is assigned to at most one participant
for j in range(n_cars):
    model += (cp.sum(assignments[:, j]) <= 1)

# 3) Only allow assignments where participant is interested in the car
for i in range(n_participants):
    for j in range(n_cars):
        if possible[i][j] == 0:
            model += (assignments[i, j] == 0)

# Objective: maximize total number of assignments
model.maximize(cp.sum(assignments))

# Solve and print
if model.solve():
    # Convert boolean matrix to integers (0/1)
    assign_val = assignments.value().tolist()
    assign_int = [[int(v) for v in row] for row in assign_val]

    solution = {
        'assignments': assign_int
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
