
import cpmpy as cp
import json

# Data (optional)
data = {
    'nbHouses': 15,
    'MarioHouse': 0,  # 0-indexed
    'LuigiHouse': 1,  # 0-indexed
    'fuelMax': 600,
    # fuel consumption between houses, conso[i][j] = fuel from i to j
    'conso': [
        [0, 221, 274, 808, 13, 677, 670, 921, 943, 969, 13, 18, 217, 86, 322],  # Mario's house
        [0, 0, 702, 83, 813, 679, 906, 246, 335, 529, 719, 528, 451, 242, 712],  # Luigi's house
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
# End of data

n = data['nbHouses']
M = data['MarioHouse']
L = data['LuigiHouse']
fuelMax = data['fuelMax']
conso = data['conso']
gold = data['goldInHouse']

# Model definition
model = cp.Model()

# Decision Variables
# s[i] is the successor of house i (s[i]==i if not in the route). For Luigi, s[L]==M.
s = cp.intvar(0, n-1, shape=n, name="s")

# inroute[i] is 1 if house i is part of Mario's route (visited), 0 otherwise
inroute = cp.boolvar(shape=n, name="inroute")

# x[i][j] = 1 iff s[i] == j (channeling matrix for convenience)
x = cp.boolvar(shape=(n, n), name="x")

# position along the path from Mario to Luigi (only meaningful for inroute nodes; Mario at 0)
pos = cp.intvar(0, n-1, shape=n, name="pos")

# Constraints

# Channeling between s and x; each row has exactly one successor
for i in range(n):
    # Exactly one successor (including possibly itself)
    model += (cp.sum(x[i, :]) == 1)
    # Channel x[i,j] <-> (s[i] == j)
    for j in range(n):
        model += (x[i, j] == (s[i] == j))

# Route membership and self-loop for non-route nodes
for i in range(n):
    # If not in route, then self-loop; if in route, no self-loop
    model += (~inroute[i]).implies(s[i] == i)
    model += inroute[i].implies(s[i] != i)

# Mario and Luigi must be in the route
model += (inroute[M] == 1)
model += (inroute[L] == 1)

# Luigi's successor must be Mario
model += (s[L] == M)

# Non-self edges only exist between route nodes
for i in range(n):
    for j in range(n):
        if i != j:
            model += (x[i, j] <= inroute[i])
            model += (x[i, j] <= inroute[j])

# In-degree constraints (counting only non-self incoming edges):
# - For Mario: exactly one incoming (from Luigi), and specifically x[L, M] == 1
# - For other nodes j != Mario: inroute[j] -> exactly one incoming; ~inroute[j] -> zero incoming
for j in range(n):
    incoming_nonself = cp.sum([x[i, j] for i in range(n) if i != j])
    if j == M:
        model += (incoming_nonself == 1)
        model += (x[L, M] == 1)
    else:
        model += (incoming_nonself == inroute[j])

# Positional ordering to enforce a single chain from Mario to Luigi
model += (pos[M] == 0)
for i in range(n):
    # Non-route nodes have pos 0; route nodes (except Mario) have pos >= 1
    model += (~inroute[i]).implies(pos[i] == 0)
    if i != M:
        model += inroute[i].implies(pos[i] >= 1)
    # For all route nodes except Luigi: pos[succ(i)] = pos[i] + 1
    if i != L:
        model += inroute[i].implies(cp.Element(pos, s[i]) == (pos[i] + 1))

# Fuel budget: sum of fuel on traversed non-self edges, excluding the artificial closing edge (Luigi->Mario)
fuel_terms = []
for i in range(n):
    for j in range(n):
        if i != j:
            if not (i == L and j == M):
                fuel_terms.append(x[i, j] * conso[i][j])
if fuel_terms:
    model += (cp.sum(fuel_terms) <= fuelMax)
else:
    # No traversed edges other than possible Luigi->Mario (edge case)
    model += (0 <= fuelMax)

# Objective: maximize gold collected in visited houses
# Gold of Mario and Luigi are zero in provided data, but included for generality
total_gold = cp.sum([inroute[i] * gold[i] for i in range(n)])
model.maximize(total_gold)

# Solve and print
if model.solve():
    solution = {'s': s.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
