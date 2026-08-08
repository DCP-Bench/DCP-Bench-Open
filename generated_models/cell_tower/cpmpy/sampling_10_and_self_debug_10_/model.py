
import cpmpy as cp
import json

# Data
input_data = {
    "delta": [
        [1, 0, 1], # delta[i][j] is 1 if site i covers region j, 0 otherwise
        [0, 1, 0]
    ],
    "cost": [3, 4], # cost[i] is the cost of building a tower at site i
    "population": [100, 200, 150], # population[j] is the population of region j
    "budget": 4 # The total budget allowed for building towers
}
# End of data

delta = input_data["delta"]
cost = input_data["cost"]
population = input_data["population"]
budget = input_data["budget"]

n_sites = len(cost)
n_regions = len(population)

# Model definition
model = cp.Model()

# Decision Variables
build_tower = cp.boolvar(shape=n_sites, name="build_tower")         # 1 if we build a tower at site i
region_covered = cp.boolvar(shape=n_regions, name="region_covered") # 1 if region j is covered

# Constraints

# Budget constraint: total cost of built towers <= budget
model += cp.sum([cost[i] * build_tower[i] for i in range(n_sites)]) <= budget

# Coverage constraints:
# A region is covered if at least one chosen site that covers it is built.
for j in range(n_regions):
    covering_sites = [i for i in range(n_sites) if delta[i][j] == 1]
    if covering_sites:
        # If a covering site is built, the region must be marked covered
        for i in covering_sites:
            model += build_tower[i].implies(region_covered[j])
        # If region_covered is true then at least one covering site must be built
        model += cp.sum([build_tower[i] for i in covering_sites]) >= region_covered[j]
    else:
        # No site can cover this region -> cannot be covered
        model += region_covered[j] == 0

# Objective: maximize total population covered
model.maximize(cp.sum([population[j] * region_covered[j] for j in range(n_regions)]))

# Solve and print
if model.solve():
    # convert boolean list to 0/1 integers
    build_tower_list = [int(v) for v in build_tower.value().tolist()]
    solution = {
        'build_tower': build_tower_list,
        'total_population_covered': int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
