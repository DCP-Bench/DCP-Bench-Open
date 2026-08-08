from cpmpy import *
import json

# Input data
num_people = 8  # number of people
compatible = [  # 1-based indexing, compatible[i] is the list of people to which i can donate
    [2, 3],
    [1, 6],
    [1, 4, 7],
    [2],
    [2],
    [5],
    [8],
    [3]
]

# Adjust to 0-based indexing
compatible = [[x - 1 for x in lst] for lst in compatible]

# Decision variables
transplants = boolvar(shape=(num_people, num_people), name="transplants")

# Model
model = Model()

# Each person can give at most one kidney
for i in range(num_people):
    model += [sum(transplants[i, :]) <= 1]

# Each person can receive at most one kidney
for j in range(num_people):
    model += [sum(transplants[:, j]) <= 1]

# A person can only donate to compatible people
for i in range(num_people):
    for j in range(num_people):
        if j not in compatible[i]:
            model += [transplants[i, j] == 0]

# A person who gives a kidney must also receive one
for i in range(num_people):
    model += [sum(transplants[i, :]) == sum(transplants[:, i])]

# Objective: maximize the number of transplants
model.maximize(sum(transplants))

# Solve the model
model.solve()

# Print the solution
solution = {"transplants": transplants.value().tolist()}
print(json.dumps(solution))