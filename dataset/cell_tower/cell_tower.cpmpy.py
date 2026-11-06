#!/usr/bin/python3
# Category: complex_or
# Source: https://github.com/xzymustbexzy/Chain-of-Experts/blob/main/dataset/ComplexOR/cell_tower

# Data

delta = [
    [1, 0, 1],  # delta[i][j] is 1 if site i covers region j, 0 otherwise
    [0, 1, 0]
]
cost = [3, 4]  # cost[i] is the cost of building a tower at site i
population = [100, 200, 150]  # population[j] is the population of region j
budget = 4  # The total budget allowed for building towers

# End of data

# Import libraries
from cpmpy import *
import json

# Data unpacking
delta = cpm_array(delta)
cost = cpm_array(cost)

num_sites = len(cost)
num_regions = len(population)

# Decision variables
build_tower = boolvar(shape=num_sites,
                      name="build_tower")  # build_tower[i] is 1 if tower at site i is built, 0 otherwise
covered_region = boolvar(shape=num_regions,
                         name="covered_region")  # covered_region[j] is 1 if region j is covered, 0 otherwise

# Model
model = Model()

# Constraint 1: A region is covered if at least one of its covering sites is selected
for j in range(num_regions):
    model += covered_region[j] <= sum([delta[i, j] * build_tower[i] for i in range(num_sites)])

# Constraint 2: The total cost of building towers does not exceed the budget
model += sum([cost[i] * build_tower[i] for i in range(num_sites)]) <= budget

# Objective: Maximize the total population covered
total_population_covered = sum(population * covered_region)
model.maximize(total_population_covered)

# Solve the model
model.solve()

# Print the solution
solution = {
    "build_tower": build_tower.value().tolist(),
    "total_population_covered": int(model.objective_value())
}
print(json.dumps(solution))
# End of CPMPy script
