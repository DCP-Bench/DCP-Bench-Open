from cpmpy import *
import json

# Parameters
n_gates = 5  # Number of gates
n_apples = n_gates + 1  # Number of apple counts (before each gate and after the last gate)

# Decision variables
apples = intvar(1, 1000, shape=n_apples, name="apples")  # Apples before each gate and after the last gate

# Model
model = Model()

# After the last gate, the boy has no apples left
model += [apples[n_gates] == 0]

# For each gate, the number of apples after the bribe is calculated
for i in range(n_gates):
    # Apples after bribe = apples_before - (half of apples_before + 1)
    # Use integer division via multiplication and subtraction
    model += [2 * apples[i + 1] == apples[i] - 2]  # Derived from apples[i] - (apples[i] // 2 + 1)

# Solve the model
model.solve()

# Print the solution
solution = {"apples": apples.value().tolist()}
print(json.dumps(solution))