from cpmpy import *
import json

# Decision variables
# cow_assignments[i] is the son (0 to 4) to whom cow i+1 is assigned
cow_assignments = intvar(0, 4, shape=25, name="cow_assignments")

# Model
model = Model()

# Number of cows assigned to each son
model += [sum(cow_assignments == 0) == 7]  # First son gets 7 cows
model += [sum(cow_assignments == 1) == 6]  # Second son gets 6 cows
model += [sum(cow_assignments == 2) == 5]  # Third son gets 5 cows
model += [sum(cow_assignments == 3) == 4]  # Fourth son gets 4 cows
model += [sum(cow_assignments == 4) == 3]  # Fifth son gets 3 cows

# Total milk produced by each son should be equal
# Milk production of cow i is i+1
# For each son, sum the milk of the cows assigned to them
milk_per_son = [sum((i + 1) * (cow_assignments[i] == j) for i in range(25)) for j in range(5)]

# All sons should have the same total milk
model += [milk_per_son[0] == milk_per_son[1]]
model += [milk_per_son[1] == milk_per_son[2]]
model += [milk_per_son[2] == milk_per_son[3]]
model += [milk_per_son[3] == milk_per_son[4]]

# Solve the model
model.solve()

# Print the solution
solution = {"cow_assignments": cow_assignments.value().tolist()}
print(json.dumps(solution))