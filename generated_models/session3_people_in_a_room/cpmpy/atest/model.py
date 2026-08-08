from cpmpy import *
import json

# Parameters
n_people = 13  # Total number of people
n_males = 4  # Number of males
n_females = n_people - n_males  # Number of females

# Decision variables
sequence = intvar(0, 1, shape=n_people, name="sequence")  # 0 for male, 1 for female

# Model
model = Model()

# Ensure exactly 4 males and 9 females in the sequence
model += [sum(sequence) == n_females]

# Ensure the ratio of females to males in the room at any one time is no greater than 7/3
# This means for any prefix of the sequence, the number of females (f) and males (m) must satisfy f/m <= 7/3
# Which is equivalent to 3*f <= 7*m
for i in range(1, n_people + 1):
    prefix = sequence[0:i]
    f = sum(prefix)
    m = i - f
    model += [3 * f <= 7 * m]

# Solve the model
model.solve()

# Print the solution
solution = {"sequence": [bool(x) for x in sequence.value().tolist()]}
print(json.dumps(solution))