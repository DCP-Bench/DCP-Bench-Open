
import cpmpy as cp
import json

# Data
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
Mario = data['MarioHouse']
Luigi = data['LuigiHouse']
fuelMax = data['fuelMax']
conso = data['conso']
gold = data['goldInHouse']

# Model definition
model = cp.Model()

# Decision Variables
# "next" represents the real route successor for modeling the path:
# For i != Luigi: next[i] == i means not visited; next[i] != i means visited and successor is next[i].
# For Luigi: next[Luigi] will be fixed to Luigi (end of the path). For printing we will set s[Luigi]=Mario as required.
next_vars = cp.intvar(0, n-1, shape=n, name="next")

# visited boolean: v[i] = 1 if house i is visited (on the path)
v = cp.boolvar(shape=n, name="v")

# rank variables to order nodes on the path, r[Mario] = 0 and ranks increase along the path until Luigi
r = cp.intvar(0, n-1, shape=n, name="r")

# Constraints

# 1) Domain and visitation linking
for i in range(n):
    if i == Luigi:
        # Luigi is visited and is the end: next[Luigi] = Luigi, but visited=1
        model += (next_vars[i] == i)
        model += (v[i] == 1)
    else:
        # visited iff next[i] != i
        model += (v[i] == (next_vars[i] != i))

# Mario must be visited and must have a successor different from itself (start of path)
model += (v[Mario] == 1)
model += (next_vars[Mario] != Mario)

# 2) Incoming constraints (exclude self-loops from counting incoming)
# For each house j, number of incoming arcs from other houses equals v[j], except Mario has indegree 0.
for j in range(n):
    incoming = []
    for i in range(n):
        if i == j:
            continue  # exclude self-loop
        incoming.append(next_vars[i] == j)
    if j == Mario:
        model += (cp.sum(incoming) == 0)
    else:
        # If v[j]==1 then exactly one predecessor points to j; if v[j]==0 then none.
        model += (cp.sum(incoming) == v[j])

# 3) Rank ordering to avoid subtours: r[Mario] = 0 and along every used arc (except from Luigi) ranks increase by 1.
model += (r[Mario] == 0)
for i in range(n):
    if i == Luigi:
        continue
    # If i is visited, then r[next[i]] == r[i] + 1
    # Use cp.Element to index r by variable next_vars[i]
    model += v[i].implies(cp.Element(r, next_vars[i]) == r[i] + 1)

# 4) Fuel constraint: sum of fuel along traveled edges (excluding Luigi -> Mario fake link) <= fuelMax
# For i != Luigi, if visited, we include conso[i][next[i]] in total fuel.
edge_costs = []
for i in range(n):
    if i == Luigi:
        continue
    # cost_i = Element(conso[i], next[i])
    cost_i = cp.Element(conso[i], next_vars[i])
    # only count if visited
    edge_costs.append(cost_i * v[i])
fuel_used = cp.sum(edge_costs)
model += (fuel_used <= fuelMax)

# Objective: maximize collected gold (sum of gold for visited houses)
total_gold = cp.sum([gold[i] * v[i] for i in range(n)])
model.maximize(total_gold)

# Solve and print
if model.solve():
    # build printed successor list s:
    s = [0] * n
    for i in range(n):
        if i == Luigi:
            # As required in the problem statement, Luigi's successor should be Mario's house
            s[i] = Mario
        else:
            s[i] = int(next_vars[i].value())
    solution = {'s': s}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
