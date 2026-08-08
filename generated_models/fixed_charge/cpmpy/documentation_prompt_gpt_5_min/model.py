
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

# profit, product type (profit, machine_index)
product = [[6, shirtM],
           [4, shortM],
           [7, pantM]]

# resource usage: labor, cloth per product
use = [[3, 4],
       [2, 3],
       [6, 4]]
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# production amounts for each product
x = cp.intvar(0, max_production, shape=num_products, name="x")
# rent machine or not
rent = cp.boolvar(shape=num_machines, name="rent")

# Constraints
# Resource capacity constraints (labor and cloth)
for r in resources:
    model += (cp.sum([use[p][r] * x[p] for p in products]) <= capacity[r])

# Link production to renting: can only produce if machine rented
for p in products:
    machine_idx = product[p][1]
    model += (x[p] <= max_production * rent[machine_idx])

# Objective: maximize profit from products minus renting costs
profit_terms = [product[p][0] * x[p] for p in products]
rent_cost_terms = [renting_cost[m] * rent[m] for m in machines]
objective = cp.sum(profit_terms) - cp.sum(rent_cost_terms)

model.maximize(objective)

# Solve and print
if model.solve():
    solution = {'z': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
