
import cpmpy as cp
import json

# Data
shirtM = 0
shortM = 1
pantM = 2
machines = [shirtM, shortM, pantM]
num_machines = len(machines)
renting_cost = [200, 150, 100]

shirt = 0
shorts = 1
pants = 2
products = [shirt, shorts, pants]
num_products = len(products)

labor = 0
cloth = 1
resources = [labor, cloth]

# capacity of labor and cloth
capacity = [150, 160]

max_production = max(capacity)

# profit, product type
product = [[6, shirtM],
           [4, shortM],
           [7, pantM]]

# resource: labor, cloth
use = [[3, 4],
       [2, 3],
       [6, 4]]
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# x[p]: number of units produced for product p
x = cp.intvar(0, max_production, shape=num_products, name="x")
# y[m]: whether machine m is rented (1) or not (0)
y = cp.boolvar(shape=num_machines, name="y")

# Constraints
# Resource capacities
for r in resources:
    model += (cp.sum([use[p][r] * x[p] for p in products]) <= capacity[r])

# Production only if corresponding machine is rented
for p in products:
    mach = product[p][1]
    model += (x[p] <= max_production * y[mach])

# Objective: maximize profit from products minus renting costs
profit_terms = [product[p][0] * x[p] for p in products]
rent_terms = [renting_cost[m] * y[m] for m in machines]
objective = cp.sum(profit_terms) - cp.sum(rent_terms)
model.maximize(objective)

# Solve and print
if model.solve():
    solution = {'z': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
