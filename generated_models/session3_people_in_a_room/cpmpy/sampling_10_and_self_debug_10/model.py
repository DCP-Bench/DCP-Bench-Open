
import cpmpy as cp
import json

# Data
num_people = 13
num_males = 4
num_females = num_people - num_males

# Model definition
model = cp.Model()

# Decision Variables
# sequence[i] = 0 if male enters at position i, 1 if female
sequence = cp.intvar(0, 1, shape=num_people, name="sequence")

# Constraints
# Exactly num_males males and num_females females in the sequence
model += cp.Count(sequence, 0) == num_males
model += cp.Count(sequence, 1) == num_females

# For each prefix of the sequence, the ratio females/males <= 7/3
# That is: females_in_prefix * 3 <= males_in_prefix * 7
# Handle the case males_in_prefix = 0 separately (then females_in_prefix must be 0)
for i in range(1, num_people + 1):
    prefix = sequence[:i]
    females_in_prefix = cp.sum(prefix)
    males_in_prefix = i - females_in_prefix
    # If males_in_prefix == 0, then females_in_prefix must be 0 (no females before any male)
    model += (males_in_prefix == 0).implies(females_in_prefix == 0)
    # If males_in_prefix > 0, then females_in_prefix * 3 <= males_in_prefix * 7
    model += (males_in_prefix > 0).implies(females_in_prefix * 3 <= males_in_prefix * 7)

# Solve and print
if model.solve():
    solution = {'sequence': sequence.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
