from cpmpy import *
import json

# Decision variables
bales = intvar(35, 50, shape=5, name="bales")

# Model
model = Model()

# All bales must be distinct
model += [AllDifferent(bales)]

# Generate all possible combinations of two bales and their weights
weights = [80, 82, 83, 84, 85, 86, 87, 88, 90, 91]
model += [sorted([bales[i] + bales[j] for i in range(5) for j in range(i + 1, 5)]) == weights]

# Solve the model
model.solve()

# Print the solution
solution = {"bales": bales.value().tolist()}
print(json.dumps(solution))