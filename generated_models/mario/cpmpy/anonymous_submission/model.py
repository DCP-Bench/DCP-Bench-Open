# Import libraries
from cpmpy import *
import json

# Parameters
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

# Decision Variables
s = intvar(0, data['nbHouses']-1, shape=data['nbHouses'], name="s")  # Successor for each house
total_fuel = intvar(0, data['fuelMax'], name="total_fuel")
total_gold = intvar(0, data['goldTotalAmount'], name="total_gold")

# Model
model = Model()

# Circuit constraint to ensure a valid path
model += Circuit(s)

# Start at Mario's house (house 1)
model += s[0] != 0  # Mario's house can't point to itself

# Calculate total fuel and gold
fuel_terms = []
gold_terms = []
for i in range(data['nbHouses']):
    for j in range(data['nbHouses']):
        if i != j:
            fuel_terms.append((s[i] == j) * data['conso'][i][j])
            gold_terms.append((s[i] == j) * data['goldInHouse'][i])

model += total_fuel == sum(fuel_terms)
model += total_gold == sum(gold_terms)

# Constraints
model += total_fuel <= data['fuelMax']
model += total_gold <= data['goldTotalAmount']

# Objective: maximize gold collected
model.maximize(total_gold)

# Solve
model.solve()

# Print solution
if model.status().exitstatus.name == 'OPTIMAL':
    solution = {
        "s": [val+1 for val in s.value().tolist()]  # Convert to 1-based indexing
    }
else:
    solution = {"s": []}  # Return empty list if no solution found
print(json.dumps(solution))