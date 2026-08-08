
from ortools.sat.python import cp_model
import json

# Input data
deck_width = 5  # Width of the deck (x dimension)
deck_length = 5  # Length of the deck (y dimension)
n_containers = 3  # Number of containers
width = [5, 2, 3]  # Widths of containers (x sizes)
length = [1, 4, 4]  # Lengths of containers (y sizes)
classes = [1, 1, 1]  # Classes of containers
# Separation constraints between classes:
# separation[c1][c2] = minimal clearance between containers of class c1 and c2
separation = [
    [0, 0],
    [0, 0]
]

# Create the model
model = cp_model.CpModel()

# Decision variables: for each container i, left[i], bottom[i] are the coordinates
# of the south-west corner. right[i], top[i] are derived.
left = []
bottom = []
right = []
top = []

for i in range(n_containers):
    # x coordinate of left edge: can be from 0 to deck_width - width[i]
    l = model.NewIntVar(0, deck_width - width[i], f"left_{i}")
    # y coordinate of bottom edge: 0 to deck_length - length[i]
    b = model.NewIntVar(0, deck_length - length[i], f"bottom_{i}")
    # right = left + width[i]
    r = model.NewIntVar(0, deck_width, f"right_{i}")
    model.Add(r == l + width[i])
    # top = bottom + length[i]
    t = model.NewIntVar(0, deck_length, f"top_{i}")
    model.Add(t == b + length[i])

    left.append(l)
    bottom.append(b)
    right.append(r)
    top.append(t)

# Non-overlap constraints for all distinct pairs
for i in range(n_containers):
    for j in range(i + 1, n_containers):
        # Boolean vars for four separation directions
        b_left = model.NewBoolVar(f"i{i}_left_of_j{j}")
        b_right = model.NewBoolVar(f"i{i}_right_of_j{j}")
        b_above = model.NewBoolVar(f"i{i}_above_j{j}")
        b_below = model.NewBoolVar(f"i{i}_below_j{j}")
        # At least one direction must hold
        model.AddBoolOr([b_left, b_right, b_above, b_below])
        # i is left of j: right[i] <= left[j] - sep
        sep = separation[classes[i]][classes[j]]
        model.Add(right[i] + sep <= left[j]).OnlyEnforceIf(b_left)
        model.Add(right[i] + sep > left[j]).OnlyEnforceIf(b_left.Not())
        # i is right of j
        model.Add(right[j] + sep <= left[i]).OnlyEnforceIf(b_right)
        model.Add(right[j] + sep > left[i]).OnlyEnforceIf(b_right.Not())
        # i is above j (i north of j)
        model.Add(top[j] + sep <= bottom[i]).OnlyEnforceIf(b_above)
        model.Add(top[j] + sep > bottom[i]).OnlyEnforceIf(b_above.Not())
        # i is below j (i south of j)
        model.Add(top[i] + sep <= bottom[j]).OnlyEnforceIf(b_below)
        model.Add(top[i] + sep > bottom[j]).OnlyEnforceIf(b_below.Not())

# Loading sequence constraints:
# For each container i >= 1, its left side must touch west wall or
# the right side of some earlier container, AND its top side must
# touch the north wall or the bottom side of some earlier container.
for i in range(1, n_containers):
    # West-touch options
    west_bools = []
    # Option 1: touches west wall
    w0 = model.NewBoolVar(f"west_wall_{i}")
    model.Add(left[i] == 0).OnlyEnforceIf(w0)
    model.Add(left[i] != 0).OnlyEnforceIf(w0.Not())
    west_bools.append(w0)
    # Options 2+: touches right[j] for some j < i
    for j in range(i):
        wj = model.NewBoolVar(f"west_cont_{i}_{j}")
        model.Add(left[i] == right[j]).OnlyEnforceIf(wj)
        model.Add(left[i] != right[j]).OnlyEnforceIf(wj.Not())
        west_bools.append(wj)
    model.AddBoolOr(west_bools)

    # North-touch options
    north_bools = []
    # Option 1: touches north wall (top == deck_length)
    n0 = model.NewBoolVar(f"north_wall_{i}")
    model.Add(top[i] == deck_length).OnlyEnforceIf(n0)
    model.Add(top[i] != deck_length).OnlyEnforceIf(n0.Not())
    north_bools.append(n0)
    # Options 2+: touches bottom[j] for some j < i
    for j in range(i):
        nj = model.NewBoolVar(f"north_cont_{i}_{j}")
        model.Add(top[i] == bottom[j]).OnlyEnforceIf(nj)
        model.Add(top[i] != bottom[j]).OnlyEnforceIf(nj.Not())
        north_bools.append(nj)
    model.AddBoolOr(north_bools)

# Create solver and solve
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'left': [solver.Value(left[i]) for i in range(n_containers)],
        'right': [solver.Value(right[i]) for i in range(n_containers)],
        'bottom': [solver.Value(bottom[i]) for i in range(n_containers)],
        'top': [solver.Value(top[i]) for i in range(n_containers)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
