from cpmpy import *
import json

# Decision variables
# Number of bags stolen for each type of coin bag
bags = intvar(0, 100, shape=6, name="bags")

# Coin bag sizes
bag_sizes = [16, 17, 23, 24, 39, 40]

# Model
model = Model()

# Total number of coins lost is 100
model += [sum(bags * bag_sizes) == 100]

# Solve the model
model.solve()

# Print the solution
solution = {"bags": bags.value().tolist()}
print(json.dumps(solution))