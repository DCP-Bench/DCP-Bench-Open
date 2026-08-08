from cpmpy import *
import json

# Parameters
n = 8  # Size of the Costas array

# Decision variables
costas = intvar(1, n, shape=n, name="costas")

# Model
model = Model()

# Ensure that costas is a permutation (i.e., all values are distinct)
model += [AllDifferent(costas)]

# Collect all ordered pairwise differences (i != j)
all_diffs = []
for i in range(n):
    for j in range(n):
        if i != j:
            all_diffs.append(costas[i] - costas[j])

# Ensure all pairwise differences are distinct
model += [AllDifferent(all_diffs)]

# Solve the model
model.solve()

# Print the solution
solution = {"costas": costas.value().tolist()}
print(json.dumps(solution))