from ortools.sat.python import cp_model
import json

# Input data
deck_width = 5  # Width of the deck
deck_length = 5  # Length of the deck
n_containers = 3  # Number of containers
width = [5, 2, 3]  # Widths of containers
length = [1, 4, 4]  # Lengths of containers
classes = [1, 1, 1]  # Classes of containers
separation = [  # Separation constraints between classes
    [0, 0],
    [0, 0]
]

# Model definition
model = cp_model.CpModel()

# Decision Variables: positions of containers on the deck
# left[i], bottom[i] are coordinates of the bottom-left corner of container i
left = [model.NewIntVar(0, deck_width - width[i], f'left_{i}') for i in range(n_containers)]
bottom = [model.NewIntVar(0, deck_length - length[i], f'bottom_{i}') for i in range(n_containers)]

# Compute right and top for each container
right = [model.NewIntVar(0, deck_width, f'right_{i}') for i in range(n_containers)]
top = [model.NewIntVar(0, deck_length, f'top_{i}') for i in range(n_containers)]

for i in range(n_containers):
    model.Add(right[i] == left[i] + width[i])
    model.Add(top[i] == bottom[i] + length[i])

# Constraints: no overlapping between containers
for i in range(n_containers):
    for j in range(i + 1, n_containers):
        # Containers i and j do not overlap: at least one of these must hold
        model.AddBoolOr([
            right[i] <= left[j],  # i is left of j
            right[j] <= left[i],  # j is left of i
            top[i] <= bottom[j],  # i is below j
            top[j] <= bottom[i]   # j is below i
        ])

# Separation constraints between classes
# For each pair of containers i, j with classes c_i, c_j, enforce minimum separation
for i in range(n_containers):
    for j in range(i + 1, n_containers):
        c_i = classes[i] - 1  # zero-based index for separation matrix
        c_j = classes[j] - 1
        sep = separation[c_i][c_j]
        if sep > 0:
            # Enforce separation horizontally or vertically
            # At least sep distance between edges if classes require separation
            # We use a disjunction to allow separation either horizontally or vertically
            model.AddBoolOr([
                right[i] + sep <= left[j],
                right[j] + sep <= left[i],
                top[i] + sep <= bottom[j],
                top[j] + sep <= bottom[i]
            ])

# Loading sequence constraints:
# Each container after the first must touch another container or deck wall to the north and west
# Touching means: either container edge aligns with deck wall or with another container edge
# For container 0 (first), it must touch deck walls to north and west:
# Since loading is from southeast corner, container 0 must be at bottom=0 (south wall) and left=0 (west wall)
model.Add(left[0] == 0)
model.Add(bottom[0] == 0)

for i in range(1, n_containers):
    # Touch to the west: left[i] == 0 (deck wall) or left[i] == right[j] for some j != i
    west_touch = []
    west_touch.append(model.NewBoolVar(f'west_wall_touch_{i}'))
    model.Add(left[i] == 0).OnlyEnforceIf(west_touch[-1])
    model.Add(left[i] != 0).OnlyEnforceIf(west_touch[-1].Not())

    west_touch_others = []
    for j in range(n_containers):
        if j == i:
            continue
        b = model.NewBoolVar(f'west_touch_{i}_{j}')
        # left[i] == right[j]
        model.Add(left[i] == right[j]).OnlyEnforceIf(b)
        model.Add(left[i] != right[j]).OnlyEnforceIf(b.Not())
        west_touch_others.append(b)

    # At least one west touch: either deck wall or some container
    model.AddBoolOr([west_touch[0]] + west_touch_others)

    # Touch to the north: bottom[i] == 0 (deck wall) or bottom[i] == top[j] for some j != i
    north_touch = []
    north_touch.append(model.NewBoolVar(f'north_wall_touch_{i}'))
    model.Add(bottom[i] == 0).OnlyEnforceIf(north_touch[-1])
    model.Add(bottom[i] != 0).OnlyEnforceIf(north_touch[-1].Not())

    north_touch_others = []
    for j in range(n_containers):
        if j == i:
            continue
        b = model.NewBoolVar(f'north_touch_{i}_{j}')
        # bottom[i] == top[j]
        model.Add(bottom[i] == top[j]).OnlyEnforceIf(b)
        model.Add(bottom[i] != top[j]).OnlyEnforceIf(b.Not())
        north_touch_others.append(b)

    # At least one north touch: either deck wall or some container
    model.AddBoolOr([north_touch[0]] + north_touch_others)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'left': [solver.Value(var) for var in left],
        'right': [solver.Value(var) for var in right],
        'top': [solver.Value(var) for var in top],
        'bottom': [solver.Value(var) for var in bottom]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")