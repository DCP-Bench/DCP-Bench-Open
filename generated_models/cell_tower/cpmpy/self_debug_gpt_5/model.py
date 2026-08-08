
import cpmpy as cp
import json

# Data (optional)
input_data = {
    "delta": [
        [1, 0, 1],  # delta[i][j] is 1 if site i covers region j, 0 otherwise
        [0, 1, 0]
    ],
    "cost": [3, 4],  # cost[i] is the cost of building a tower at site i
    "population": [100, 200, 150],  # population[j] is the population of region j
    "budget": 4  # The total budget allowed for building towers
}
# End of data

delta = input_data["delta"]
cost = input_data["cost"]
population = input_data["population"]
budget = input_data["budget"]

n_sites = len(delta)
n_regions = len(population)

# Model definition
model = cp.Model()

# Decision Variables
build_tower = cp.boolvar(shape=n_sites, name="build_tower")
covered = cp.boolvar(shape=n_regions, name="covered")

# Constraints

# Budget constraint: sum of costs of built towers <= budget
model += (cp.sum([build_tower[i] * cost[i] for i in range(n_sites)]) <= budget)

# Coverage constraints: a region is covered if any tower that covers it is built
for j in range(n_regions):
    covering_sites = [build_tower[i] for i in range(n_sites) if delta[i][j] == 1]
    if len(covering_sites) == 0:
        model += (covered[j] == 0)
    else:
        model += (covered[j] == cp.any(covering_sites))

# Objective (optional)
# Maximize total population covered
objective = cp.sum([covered[j] * population[j] for j in range(n_regions)])
model.maximize(objective)

# Solve and print
if model.solve():
    build_tower_list = [int(v) for v in build_tower.value().tolist()]
    solution = {
        'build_tower': build_tower_list,
        'total_population_covered': int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
