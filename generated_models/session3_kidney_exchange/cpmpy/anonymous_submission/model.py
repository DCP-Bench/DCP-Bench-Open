from cpmpy import *
import json

# Parameters
num_people = 8
compatible = [
    [2, 3],
    [1, 6],
    [1, 4, 7],
    [2],
    [2],
    [5],
    [8],
    [3]
]

# Decision Variables
transplants = boolvar(shape=(num_people, num_people), name="transplants")  # transplants[i][j] is 1 if i donates to j

# Model
model = Model()

# Constraints
# No self-donation
for i in range(num_people):
    model += transplants[i][i] == 0

# Only donate to compatible people
for i in range(num_people):
    for j in range(num_people):
        if (j+1) not in compatible[i]:  # +1 because of 1-based indexing in input
            model += transplants[i][j] == 0

# Each person can receive at most one kidney
for j in range(num_people):
    model += sum(transplants[i][j] for i in range(num_people)) <= 1

# If a person donates, they must receive a kidney
for i in range(num_people):
    model += (sum(transplants[i][j] for j in range(num_people)) == 
              sum(transplants[k][i] for k in range(num_people)))

# Objective: maximize the number of transplants (which equals the number of people receiving kidneys)
model.maximize(sum(transplants.flatten()))

# Solve
model.solve()

# Print solution
solution = {
    "transplants": transplants.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script