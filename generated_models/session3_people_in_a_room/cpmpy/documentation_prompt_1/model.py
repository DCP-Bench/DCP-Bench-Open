
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
model += (cp.sum(sequence) == num_females)
model += (cp.sum(1 - sequence) == num_males)

# At any time, ratio of females to males in the room <= 7/3
# For each prefix i, females_i / males_i <= 7/3
# Handle division carefully: females_i * 3 <= males_i * 7
# Also, males_i > 0 to avoid division by zero; if males_i == 0, ratio is infinite, so females_i must be 0
for i in range(num_people):
    females_i = cp.sum(sequence[:i+1])
    males_i = (i + 1) - females_i
    # If males_i == 0, then females_i must be 0 (no females before any male)
    model += cp.IfThenElse(males_i == 0, females_i == 0, females_i * 3 <= males_i * 7)

# Solve and print
if model.solve():
    solution = {'sequence': sequence.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
