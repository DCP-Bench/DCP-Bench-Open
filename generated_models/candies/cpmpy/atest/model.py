from cpmpy import *
import json

# Input data
ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4]  # Ratings of the children
num_children = len(ratings)

# Decision variables
# candies[i] = number of candies given to child i
candies = intvar(1, 100, shape=num_children, name="candies")

# Model
model = Model()

# Each child must get at least 1 candy
model += [candies >= 1]

# If a child has a higher rating than the left neighbor, they must get more candies
for i in range(1, num_children):
    model += (ratings[i] > ratings[i - 1]).implies(candies[i] > candies[i - 1])

# If a child has a higher rating than the right neighbor, they must get more candies
for i in range(num_children - 1):
    model += (ratings[i] > ratings[i + 1]).implies(candies[i] > candies[i + 1])

# Objective: minimize the total number of candies
total_candies = sum(candies)
model.minimize(total_candies)

# Solve the model
model.solve()

# Print the solution
solution = {"z": total_candies.value()}
print(json.dumps(solution))