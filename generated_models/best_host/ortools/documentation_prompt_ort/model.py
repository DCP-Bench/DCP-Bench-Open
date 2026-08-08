from ortools.sat.python import cp_model
import json

# Guests indexed as:
# 0: Andrew
# 1: Betty
# 2: Cara
# 3: Dave
# 4: Erica
# 5: Frank

# Allowed neighbors for each guest (by index):
allowed_neighbors = {
    0: {3, 5},       # Andrew only next to Dave(3) and Frank(5)
    1: {2, 4},       # Betty only next to Cara(2) and Erica(4)
    2: {1, 5},       # Cara only next to Betty(1) and Frank(5)
    3: {0, 4},       # Dave only next to Andrew(0) and Erica(4)
    4: {1, 3},       # Erica only next to Betty(1) and Dave(3)
    5: {0, 2}        # Frank only next to Andrew(0) and Cara(2)
}

model = cp_model.CpModel()

num_guests = 6
# Decision variables: x[i] is the guest seated at position i (0 to 5)
x = [model.NewIntVar(0, num_guests - 1, f'x{i}') for i in range(num_guests)]

# All guests must be seated exactly once
model.AddAllDifferent(x)

# Since the table is circular, neighbors are (i, i+1 mod 6)
# We want to minimize conflicts: neighbors who are not allowed neighbors

# Create boolean variables conflict[i] indicating if there is conflict between seat i and seat (i+1)%6
conflict = []
for i in range(num_guests):
    c = model.NewBoolVar(f'conflict_{i}')
    conflict.append(c)

# Add constraints for conflicts
for i in range(num_guests):
    guest1 = x[i]
    guest2 = x[(i + 1) % num_guests]

    # conflict[i] = 1 if guest2 not in allowed_neighbors[guest1]
    # We implement this by creating allowed pairs and using AllowedAssignments

    # Create allowed pairs for guest1: (guest1, allowed_neighbor)
    allowed_pairs = []
    for g1 in range(num_guests):
        for g2 in range(num_guests):
            # If g2 in allowed_neighbors[g1], then no conflict (conflict=0)
            # else conflict=1
            if g2 in allowed_neighbors[g1]:
                allowed_pairs.append((g1, g2, 0))
            else:
                allowed_pairs.append((g1, g2, 1))

    # We need to link guest1, guest2, and conflict[i]
    # Create a variable tuple (guest1, guest2, conflict[i]) and enforce allowed assignments
    model.AddAllowedAssignments([guest1, guest2, conflict[i]], allowed_pairs)

# Objective: minimize total conflicts
model.Minimize(sum(conflict))

solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'x': [solver.Value(var) for var in x]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")