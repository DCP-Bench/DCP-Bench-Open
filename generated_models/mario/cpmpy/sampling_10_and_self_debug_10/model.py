
import cpmpy as cp
import json
import numpy as np

# Data
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
# End of data

nbHouses = data['nbHouses']
MarioHouse = data['MarioHouse'] - 1  # zero-based index
LuigiHouse = data['LuigiHouse'] - 1  # zero-based index
fuelMax = data['fuelMax']
conso = np.array(data['conso'])
goldInHouse = data['goldInHouse']

model = cp.Model()

# Decision variables:
# s[i] = successor house of house i (0-based index)
# The successor of LuigiHouse is itself (end)
s = cp.intvar(0, nbHouses - 1, shape=nbHouses, name="s")

# order[i] = visiting order of house i, nbHouses means not visited
order = cp.intvar(0, nbHouses, shape=nbHouses, name="order")

# Constraints:

# 1) The successor of LuigiHouse is LuigiHouse itself (end of route)
model += (s[LuigiHouse] == LuigiHouse)

# 2) The successor of MarioHouse cannot be MarioHouse (no loop start)
model += (s[MarioHouse] != MarioHouse)

# 3) No house can point to MarioHouse (start) except LuigiHouse pointing to itself
for i in range(nbHouses):
    if i != LuigiHouse:
        model += (s[i] != MarioHouse)

# 4) Order constraints
model += (order[MarioHouse] == 0)
model += (order[LuigiHouse] > 0)
model += (order[LuigiHouse] <= nbHouses - 1)

for i in range(nbHouses):
    if i != LuigiHouse:
        model += ((order[i] < order[LuigiHouse]) | (order[i] == nbHouses))

# 5) Successor and order relation
for i in range(nbHouses):
    if i != LuigiHouse:
        bools = []
        for j in range(nbHouses):
            b = (s[i] == j)
            bools.append(b)
            model += b.implies(order[j] == order[i] + 1)
        model += cp.sum(bools) == 1
    else:
        model += (s[i] == i)

# 6) Fuel consumption constraint using cp.Element
fuel_used = cp.intvar(0, 1000000, name="fuel_used")

# For each house except LuigiHouse, define fuel_i = conso[i][s[i]]
fuel_i_vars = []
for i in range(nbHouses):
    if i != LuigiHouse:
        fuel_i = cp.intvar(0, np.max(conso), name=f"fuel_{i}")
        model += (fuel_i == cp.Element(conso[i], s[i]))
        fuel_i_vars.append(fuel_i)

model += (fuel_used == cp.sum(fuel_i_vars))
model += (fuel_used <= fuelMax)

# 7) Gold collected
gold_collected = cp.intvar(0, 1000000, name="gold_collected")
model += (gold_collected == cp.sum([goldInHouse[i] * (order[i] != nbHouses) for i in range(nbHouses)]))

model.maximize(gold_collected)

# Solve and print
if model.solve():
    s_sol = [int(s[i].value()) + 1 for i in range(nbHouses)]
    solution = {'s': s_sol}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
