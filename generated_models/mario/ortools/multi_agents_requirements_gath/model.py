import json
from ortools.sat.python import cp_model

# ---------------------
# Input data (immutable)
# ---------------------

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

# ---------------------
# Model creation
# ---------------------

nb = data['nbHouses']
start = data['MarioHouse']
end = data['LuigiHouse']
fuel_max = data['fuelMax']
c = data['conso']
G = data['goldInHouse']

model = cp_model.CpModel()

# Binary arc variables x[i][j] for i != j
x = {}
for i in range(nb):
    for j in range(nb):
        if i == j:
            continue
        x[i, j] = model.NewBoolVar(f'x_{i}_{j}')

# Visit indicator y[i]
y = [model.NewBoolVar(f'y_{i}') for i in range(nb)]

# MTZ ordering variables u[i]
# They need integer domain 0..nb
u = [model.NewIntVar(0, nb, f'u_{i}') for i in range(nb)]

# ---------------------
# Constraints
# ---------------------

# 1. Self-loops forbidden (already no variable for i==j)

# 2. Start node degree constraints
model.Add(sum(x[start, j] for j in range(nb) if j != start) == 1)
model.Add(sum(x[i, start] for i in range(nb) if i != start) == 0)

# 3. End node degree constraints
model.Add(sum(x[i, end] for i in range(nb) if i != end) == 1)
model.Add(sum(x[end, j] for j in range(nb) if j != end) == 0)

# 4. Intermediate nodes: in-degree = out-degree = y[i]
for i in range(nb):
    if i in (start, end):
        continue
    in_deg = sum(x[j, i] for j in range(nb) if j != i)
    out_deg = sum(x[i, j] for j in range(nb) if j != i)
    model.Add(in_deg == y[i])
    model.Add(out_deg == y[i])
    # Equality between in and out automatically implied but add explicitly
    model.Add(in_deg == out_deg)

# 5. Mandatory visits to start and end
model.Add(y[start] == 1)
model.Add(y[end] == 1)

# 6. Link arcs to y for start and end (optional but tighten)
#    Start: out-degree 1, in-degree 0, so y[start] already 1.
#    End: in-degree 1, out-degree 0.

# 7. Fuel budget
fuel_consumption = []
coefficients = []
for (i, j), var in x.items():
    fuel_consumption.append(var)
    coefficients.append(c[i][j])
model.Add(sum(coefficients[k] * fuel_consumption[k] for k in range(len(fuel_consumption))) <= fuel_max)

# 8. MTZ subtour elimination (path version)
model.Add(u[start] == 0)
for i in range(nb):
    if i == start:
        continue
    model.Add(u[i] >= 0)
    model.Add(u[i] <= nb)

big_M = nb
for i in range(nb):
    for j in range(nb):
        if i == j:
            continue
        # u_j >= u_i + 1 - big_M * (1 - x_ij)
        model.Add(u[j] >= u[i] + 1 - big_M * (1 - x[i, j]))

# 9. Link y with arcs for start and end to keep model tight
#    y[end] already 1. Ensure arcs linking.
model.Add(sum(x[j, end] for j in range(nb) if j != end) == 1)  # already exists
model.Add(sum(x[start, j] for j in range(nb) if j != start) == 1)  # already exists

# 10. Visit indicators for start and end fixed to 1 (already done)

# 11. Out/In degree bound for start and end vs y (tightening)
model.Add(sum(x[start, j] for j in range(nb) if j != start) <= y[start])
model.Add(sum(x[j, end] for j in range(nb) if j != end) <= y[end])

# ---------------------
# Objective: Maximize collected gold
# ---------------------

model.Maximize(sum(G[i] * y[i] for i in range(nb)))

# ---------------------
# Solve
# ---------------------

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30  # safety limit
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    # In the very unlikely event that no solution is found, still output identity successors
    s = list(range(nb))
    print(json.dumps({'s': s}))
    exit()

# ---------------------
# Extract successor list s
# ---------------------

s = [i for i in range(nb)]  # default self-loops
for i in range(nb):
    for j in range(nb):
        if i == j:
            continue
        if solver.Value(x[i, j]):
            s[i] = j
            break  # unique successor
# Ensure Luigi (end) has self-loop
s[end] = end

print(json.dumps({'s': s}))
