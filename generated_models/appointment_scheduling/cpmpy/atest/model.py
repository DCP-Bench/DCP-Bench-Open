from cpmpy import *
import json

# Input data
m = [
    [1, 1, 1, 1],
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 1]
]  # Matrix representing the free-busy schedules

# Parameters
n_people = len(m)  # Number of people
n_slots = len(m[0])  # Number of interview slots

# Decision variables
x = boolvar(shape=(n_people, n_slots), name="x")

# Model
model = Model()

# Each slot must have exactly one person assigned
for slot in range(n_slots):
    model += [sum(x[:, slot]) == 1]

# Each person can be assigned to at most one slot
for person in range(n_people):
    model += [sum(x[person, :]) <= 1]

# A person can only be assigned to a slot if they are free in that slot
for person in range(n_people):
    for slot in range(n_slots):
        model += [x[person, slot] <= m[person][slot]]

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))