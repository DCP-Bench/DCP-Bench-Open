from ortools.sat.python import cp_model
import json

# Input data
data = {
    'nbHouses': 15,
    'MarioHouse': 1,
    'LuigiHouse': 2,
    'fuelMax': 2000,
    'goldTotalAmount': 1500,
    'conso': [
        [0, 221, 274, 808, 13, 677, 670, 921, 943, 969, 13, 18, 217, 86, 322],
        [0, 0, 702, 83, 813, 679, 906, 246, 335, 529, 719, 528, 451, 242, 712],
        [274, 702, 0, 127, 110, 72, 835, 5, 161, 430, 686, 664, 799, 523, 73],
        [808, 83, 127, 0, 717, 80, 31, 71, 683, 668, 248, 826, 916, 467, 753],
        [13, 813, 110, 717, 0, 951, 593, 579, 706, 579, 101, 551, 280, 414, 294],
        [677, 679, 72, 80, 951, 0, 262, 12, 138, 222, 146, 571, 907, 225, 938],
        [670, 906, 835, 31, 593, 262, 0, 189, 558, 27, 287, 977, 226, 454, 501],
        [921, 246, 5, 71, 579, 12, 189, 0, 504, 221, 483, 226, 38, 314, 118],
        [943, 335, 161, 683, 706, 138, 558, 504, 0, 949, 393, 721, 267, 167, 420],
        [969, 529, 430, 668, 579, 222, 27, 221, 949, 0, 757, 747, 980, 589, 528],
        [13, 719, 686, 248, 101, 146, 287, 483, 393, 757, 0, 633, 334, 492, 859],
        [18, 528, 664, 826, 551, 571, 977, 226, 721, 747, 633, 0, 33, 981, 375],
        [217, 451, 799, 916, 280, 907, 226, 38, 267, 980, 334, 33, 0, 824, 491],
        [86, 242, 523, 467, 414, 225, 454, 314, 167, 589, 492, 981, 824, 0, 143],
        [322, 712, 73, 753, 294, 938, 501, 118, 420, 528, 859, 375, 491, 143, 0]
    ],
    'goldInHouse': [0, 0, 40, 67, 89, 50, 6, 19, 47, 68, 94, 86, 34, 14, 14]
}

nbHouses = data['nbHouses']
MarioHouse = data['MarioHouse'] - 1  # zero-based index
LuigiHouse = data['LuigiHouse'] - 1  # zero-based index
fuelMax = data['fuelMax']
conso = data['conso']
goldInHouse = data['goldInHouse']

model = cp_model.CpModel()

# Decision variables:
# s[i] = successor house of house i (0-based index)
s = [model.NewIntVar(0, nbHouses - 1, f's_{i}') for i in range(nbHouses)]

# We want to model a path from MarioHouse to LuigiHouse visiting houses without cycles except the end.
# The path starts at MarioHouse and ends at LuigiHouse.
# LuigiHouse has no successor (we can set s[LuigiHouse] = LuigiHouse to indicate end).

# Add constraint that LuigiHouse is the end (no successor)
model.Add(s[LuigiHouse] == LuigiHouse)

# To avoid cycles and ensure a path, we use a circuit constraint.
# Circuit constraint requires arcs in the form (tail, head, literal)
# We create arcs for all possible edges except from LuigiHouse (which has no successor except itself).

# Create literals for arcs
arc_literals = {}
for i in range(nbHouses):
    for j in range(nbHouses):
        # Allow self-loop only for LuigiHouse
        if i == LuigiHouse and j == LuigiHouse:
            continue
        # No self-loop except LuigiHouse
        if i == j and i != LuigiHouse:
            continue
        arc_literals[(i, j)] = model.NewBoolVar(f'arc_{i}_{j}')

# Add exactly one successor for each house except LuigiHouse
for i in range(nbHouses):
    if i == LuigiHouse:
        # Already fixed s[LuigiHouse] == LuigiHouse
        continue
    model.AddExactlyOne(arc_literals[(i, j)] for j in range(nbHouses) if (i, j) in arc_literals)

# Link s[i] with arc_literals
for i in range(nbHouses):
    if i == LuigiHouse:
        continue
    # s[i] == j <=> arc_literals[(i,j)] == True
    # We enforce equivalence by:
    # s[i] == j => arc_literals[(i,j)] == True
    # arc_literals[(i,j)] == True => s[i] == j
    # We do this by reification constraints
    for j in range(nbHouses):
        if (i, j) not in arc_literals:
            continue
        model.Add(s[i] == j).OnlyEnforceIf(arc_literals[(i, j)])
        model.Add(s[i] != j).OnlyEnforceIf(arc_literals[(i, j)].Not())

# Circuit constraint to ensure the arcs form a single cycle covering all nodes except LuigiHouse
# We create a list of arcs for the circuit constraint
# The circuit constraint requires arcs in the form of (tail, head, literal)
# We add the self-loop arc for LuigiHouse with literal True
arc_list = []
for (i, j), lit in arc_literals.items():
    arc_list.append(cp_model.Arc(i, j, lit))
# Add self-loop arc for LuigiHouse with literal True
arc_list.append(cp_model.Arc(LuigiHouse, LuigiHouse, model.NewConstant(1)))

model.AddCircuit(arc_list)

# The path must start at MarioHouse
# We enforce that no other house points to MarioHouse (except LuigiHouse can point to itself)
# So MarioHouse has no incoming arcs except from LuigiHouse if LuigiHouse == MarioHouse (not the case here)
# We enforce that MarioHouse has no incoming arcs except from LuigiHouse if any
for i in range(nbHouses):
    if i == MarioHouse:
        continue
    # sum of arcs (i -> MarioHouse) == 0
    if (i, MarioHouse) in arc_literals:
        model.Add(arc_literals[(i, MarioHouse)] == 0)

# Fuel consumption calculation
# We sum the fuel consumption for each arc chosen
fuel_consumption = model.NewIntVar(0, fuelMax, 'fuel_consumption')
fuel_terms = []
for (i, j), lit in arc_literals.items():
    fuel_terms.append(lit * conso[i][j])
model.Add(fuel_consumption == sum(fuel_terms))
model.Add(fuel_consumption <= fuelMax)

# Gold collected is sum of gold in visited houses except MarioHouse (start) and LuigiHouse (end)
# We create a boolean variable visited[i] indicating if house i is visited (except MarioHouse and LuigiHouse)
visited = []
for i in range(nbHouses):
    if i == MarioHouse or i == LuigiHouse:
        visited.append(model.NewConstant(0))
    else:
        # visited[i] = 1 if some arc points to i (i.e. i is visited)
        incoming_arcs = []
        for k in range(nbHouses):
            if (k, i) in arc_literals:
                incoming_arcs.append(arc_literals[(k, i)])
        if incoming_arcs:
            visited_i = model.NewBoolVar(f'visited_{i}')
            model.AddMaxEquality(visited_i, incoming_arcs)
            visited.append(visited_i)
        else:
            visited.append(model.NewConstant(0))

gold_collected = model.NewIntVar(0, data['goldTotalAmount'], 'gold_collected')
model.Add(gold_collected == sum(visited[i] * goldInHouse[i] for i in range(nbHouses)))

# Objective: maximize gold collected
model.Maximize(gold_collected)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # Extract successors s as list of 15 integers (1-based indexing)
    s_sol = [solver.Value(s[i]) + 1 for i in range(nbHouses)]
    solution = {'s': s_sol}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")